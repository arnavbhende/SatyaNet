// Test file to verify SocietalImpact component handles null properly
import SocietalImpact from './SocietalImpact';

// Test cases
const testCases = [
  { impact: null, description: "null impact" },
  { impact: undefined, description: "undefined impact" },
  { impact: {
    impact_level: "HIGH" as const,
    impact_score: 0.8,
    impact_explanation: "Test explanation",
    recommended_action: "Test action"
  }, description: "valid impact" }
];

console.log("SocietalImpact component test cases:");
testCases.forEach((testCase, index) => {
  console.log(`Test ${index + 1}: ${testCase.description}`);
  console.log("Input:", testCase.impact);
  // This would be tested in a test environment
  // <SocietalImpact impact={testCase.impact} />
});

export default function TestComponent() {
  return (
    <div>
      <h2>SocietalImpact Component Tests</h2>
      {testCases.map((testCase, index) => (
        <div key={index} style={{ marginBottom: '20px' }}>
          <h3>Test {index + 1}: {testCase.description}</h3>
          <SocietalImpact impact={testCase.impact} />
        </div>
      ))}
    </div>
  );
}
