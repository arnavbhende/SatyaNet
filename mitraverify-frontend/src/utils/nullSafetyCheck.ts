/**
 * Utility functions for null safety checks
 */

export const safeGet = <T, K extends keyof T>(
  obj: T | null | undefined,
  key: K,
  defaultValue: any
): any => {
  return obj?.[key] ?? defaultValue;
};

export const safeString = (value: string | null | undefined, defaultValue: string = ""): string => {
  return value ?? defaultValue;
};

export const safeNumber = (value: number | null | undefined, defaultValue: number = 0): number => {
  return value ?? defaultValue;
};

export const hasSocietalImpact = (result: any): boolean => {
  return !!(result?.societal_impact && 
    typeof result.societal_impact === 'object' && 
    result.societal_impact !== null);
};

export const getSocietalImpactSafely = (result: any) => {
  if (!hasSocietalImpact(result)) {
    return null;
  }
  
  return {
    impact_level: safeString(result.societal_impact?.impact_level, "UNKNOWN"),
    impact_score: safeNumber(result.societal_impact?.impact_score, 0),
    impact_explanation: safeString(result.societal_impact?.impact_explanation, "No explanation available"),
    recommended_action: safeString(result.societal_impact?.recommended_action, "No action recommended")
  };
};
