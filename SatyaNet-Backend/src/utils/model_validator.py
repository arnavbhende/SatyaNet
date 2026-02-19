"""
Model Validation and Testing Utilities
"""
import torch
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import json

logger = logging.getLogger(__name__)

class ModelValidator:
    """Utilities for validating model performance and outputs"""
    
    @staticmethod
    def validate_model_output(model_output: Dict[str, Any], expected_keys: List[str]) -> bool:
        """Validate that model output contains expected keys and valid values"""
        # Check required keys
        for key in expected_keys:
            if key not in model_output:
                logger.error(f"Missing required key in model output: {key}")
                return False
        
        # Validate prediction values
        if 'prediction' in model_output:
            valid_predictions = ['reliable', 'misinformation', 'unknown', 'error']
            if model_output['prediction'] not in valid_predictions:
                logger.error(f"Invalid prediction value: {model_output['prediction']}")
                return False
        
        # Validate confidence
        if 'confidence' in model_output:
            confidence = model_output['confidence']
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                logger.error(f"Invalid confidence value: {confidence}")
                return False
        
        # Validate probabilities
        if 'probabilities' in model_output:
            probs = model_output['probabilities']
            if not isinstance(probs, dict):
                logger.error("Probabilities must be a dictionary")
                return False
            
            total_prob = sum(probs.values())
            if not np.isclose(total_prob, 1.0, atol=0.01):
                logger.error(f"Probabilities must sum to 1.0, got {total_prob}")
                return False
        
        return True
    
    @staticmethod
    def calculate_model_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
        """Calculate comprehensive model performance metrics"""
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        
        # Additional metrics
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "specificity": float(specificity),
            "sensitivity": float(sensitivity),
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn)
        }
    
    @staticmethod
    def validate_text_input(text: str, min_length: int = 10, max_length: int = 10000) -> Dict[str, Any]:
        """Validate text input for model processing"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check length
        if len(text) < min_length:
            result["is_valid"] = False
            result["errors"].append(f"Text too short: {len(text)} < {min_length}")
        
        if len(text) > max_length:
            result["warnings"].append(f"Text very long: {len(text)} > {max_length}")
        
        # Check for empty or whitespace-only text
        if not text.strip():
            result["is_valid"] = False
            result["errors"].append("Text is empty or contains only whitespace")
        
        # Check for non-printable characters
        non_printable = [c for c in text if not c.isprintable() and not c.isspace()]
        if non_printable:
            result["warnings"].append(f"Text contains {len(non_printable)} non-printable characters")
        
        return result
    
    @staticmethod
    def benchmark_model_consistency(model, test_inputs: List[str], num_runs: int = 5) -> Dict[str, Any]:
        """Test model consistency across multiple runs"""
        results = []
        
        for text in test_inputs:
            run_results = []
            
            for _ in range(num_runs):
                try:
                    result = model.analyze_text(text)
                    if result.get("prediction") != "error":
                        run_results.append({
                            "prediction": result["prediction"],
                            "confidence": result["confidence"]
                        })
                except Exception as e:
                    logger.warning(f"Error in consistency test: {e}")
            
            if run_results:
                # Calculate consistency metrics
                predictions = [r["prediction"] for r in run_results]
                confidences = [r["confidence"] for r in run_results]
                
                prediction_consistency = len(set(predictions)) == 1
                confidence_variance = np.var(confidences)
                confidence_std = np.std(confidences)
                
                results.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "prediction_consistency": prediction_consistency,
                    "confidence_variance": float(confidence_variance),
                    "confidence_std": float(confidence_std),
                    "avg_confidence": float(np.mean(confidences)),
                    "predictions": predictions
                })
        
        return {
            "consistency_results": results,
            "overall_consistency": sum(r["prediction_consistency"] for r in results) / len(results) if results else 0
        }
    
    @staticmethod
    def generate_validation_report(model_name: str, metrics: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report"""
        report = f"""
# Model Validation Report
## Model: {model_name}

## Performance Metrics
- **Accuracy**: {metrics.get('accuracy', 'N/A'):.3f}
- **Precision**: {metrics.get('precision', 'N/A'):.3f}
- **Recall**: {metrics.get('recall', 'N/A'):.3f}
- **F1 Score**: {metrics.get('f1_score', 'N/A'):.3f}
- **Specificity**: {metrics.get('specificity', 'N/A'):.3f}
- **Sensitivity**: {metrics.get('sensitivity', 'N/A'):.3f}

## Confusion Matrix
- **True Positives**: {metrics.get('true_positives', 'N/A')}
- **True Negatives**: {metrics.get('true_negatives', 'N/A')}
- **False Positives**: {metrics.get('false_positives', 'N/A')}
- **False Negatives**: {metrics.get('false_negatives', 'N/A')}

## Recommendations
"""
        
        # Add recommendations based on metrics
        accuracy = metrics.get('accuracy', 0)
        precision = metrics.get('precision', 0)
        recall = metrics.get('recall', 0)
        
        if accuracy < 0.8:
            report += "- ⚠️ **Low accuracy detected** - Consider retraining with more data\n"
        
        if precision < 0.7:
            report += "- ⚠️ **Low precision detected** - Model may have too many false positives\n"
        
        if recall < 0.7:
            report += "- ⚠️ **Low recall detected** - Model may miss many actual cases\n"
        
        if accuracy >= 0.9 and precision >= 0.9 and recall >= 0.9:
            report += "- ✅ **Excellent performance** - Model is ready for production\n"
        
        return report

# Global validator instance
model_validator = ModelValidator()
