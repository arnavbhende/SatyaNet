"""
Model Training Pipeline for Misinformation Detection
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

logger = logging.getLogger(__name__)

class MisinformationDataset(Dataset):
    """Custom dataset for misinformation detection"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class TrainingPipeline:
    """Complete training pipeline for misinformation detection models"""
    
    def __init__(self, model_name: str = "google/muril-base-cased"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.training_history = []
    
    def setup_model(self, num_labels: int = 2):
        """Initialize model and tokenizer"""
        logger.info(f"Setting up model: {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels
        )
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.pad_token_id
        
        self.model.to(self.device)
        logger.info("Model setup complete")
    
    def prepare_data(self, data_path: str, test_size: float = 0.2, random_state: int = 42) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Prepare training, validation, and test data loaders"""
        logger.info(f"Loading data from: {data_path}")
        
        # Load data (assuming JSON format)
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = [item['text'] for item in data]
        labels = [item['label'] for item in data]
        
        # Split data
        train_texts, temp_texts, train_labels, temp_labels = train_test_split(
            texts, labels, test_size=test_size * 2, random_state=random_state, stratify=labels
        )
        
        val_texts, test_texts, val_labels, test_labels = train_test_split(
            temp_texts, temp_labels, test_size=0.5, random_state=random_state, stratify=temp_labels
        )
        
        # Create datasets
        train_dataset = MisinformationDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = MisinformationDataset(val_texts, val_labels, self.tokenizer)
        test_dataset = MisinformationDataset(test_texts, test_labels, self.tokenizer)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
        
        logger.info(f"Data prepared - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader
    
    def train_epoch(self, train_loader: DataLoader, optimizer, scheduler) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        num_batches = 0
        
        for batch in train_loader:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches
        return {"train_loss": avg_loss}
    
    def validate_epoch(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        num_batches = 0
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                num_batches += 1
                
                predictions = torch.argmax(outputs.logits, dim=1)
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        avg_loss = total_loss / num_batches
        
        # Calculate accuracy
        accuracy = np.mean(np.array(all_predictions) == np.array(all_labels))
        
        return {"val_loss": avg_loss, "val_accuracy": accuracy}
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              num_epochs: int = 3, learning_rate: float = 2e-5) -> Dict[str, List[float]]:
        """Full training loop"""
        logger.info(f"Starting training for {num_epochs} epochs")
        
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=0.0, total_iters=num_epochs)
        
        history = {"train_loss": [], "val_loss": [], "val_accuracy": []}
        
        for epoch in range(num_epochs):
            logger.info(f"Epoch {epoch + 1}/{num_epochs}")
            
            # Train
            train_metrics = self.train_epoch(train_loader, optimizer, scheduler)
            
            # Validate
            val_metrics = self.validate_epoch(val_loader)
            
            # Record history
            history["train_loss"].append(train_metrics["train_loss"])
            history["val_loss"].append(val_metrics["val_loss"])
            history["val_accuracy"].append(val_metrics["val_accuracy"])
            
            logger.info(f"Train Loss: {train_metrics['train_loss']:.4f}, "
                       f"Val Loss: {val_metrics['val_loss']:.4f}, "
                       f"Val Acc: {val_metrics['val_accuracy']:.4f}")
        
        self.training_history = history
        return history
    
    def evaluate(self, test_loader: DataLoader) -> Dict[str, Any]:
        """Evaluate model on test set"""
        logger.info("Evaluating model on test set")
        
        self.model.eval()
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                predictions = torch.argmax(outputs.logits, dim=1)
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # Generate classification report
        report = classification_report(all_labels, all_predictions, output_dict=True)
        
        return {
            "classification_report": report,
            "predictions": all_predictions,
            "true_labels": all_labels
        }
    
    def save_model(self, save_path: str):
        """Save trained model and tokenizer"""
        logger.info(f"Saving model to: {save_path}")
        
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        # Save training history
        with open(save_path / "training_history.json", 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        logger.info("Model saved successfully")
    
    def load_model(self, model_path: str):
        """Load trained model and tokenizer"""
        logger.info(f"Loading model from: {model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        
        # Load training history if available
        history_path = Path(model_path) / "training_history.json"
        if history_path.exists():
            with open(history_path, 'r') as f:
                self.training_history = json.load(f)
        
        logger.info("Model loaded successfully")

# Global training pipeline instance
training_pipeline = TrainingPipeline()
