"use client";

import { AlertTriangle, Shield, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface SocietalImpactData {
  impact_level: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  impact_score: number;
  impact_explanation: string;
  recommended_action: string;
}

interface SocietalImpactProps {
  impact: SocietalImpactData | null | undefined;
}

export default function SocietalImpact({ impact }: SocietalImpactProps) {
  if (!impact) {
    return (
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Potential Societal Impact
          </CardTitle>
          <CardDescription>
            Assessment of potential societal harm if content is misinformation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-gray-500">
            Societal impact analysis not available
          </div>
        </CardContent>
      </Card>
    );
  }

  const getImpactColor = (level: string) => {
    switch (level) {
      case "HIGH":
        return "text-red-600";
      case "MEDIUM":
        return "text-yellow-600";
      case "LOW":
        return "text-green-600";
      default:
        return "text-gray-600";
    }
  };

  const getBadgeVariant = (level: string) => {
    switch (level) {
      case "HIGH":
        return "destructive" as const;
      case "MEDIUM":
        return "secondary" as const;
      case "LOW":
        return "default" as const;
      default:
        return "outline" as const;
    }
  };

  const getImpactIcon = (level: string) => {
    switch (level) {
      case "HIGH":
        return <AlertTriangle className="h-4 w-4" />;
      case "MEDIUM":
        return <Shield className="h-4 w-4" />;
      case "LOW":
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Shield className="h-4 w-4" />;
    }
  };

  const impactColor = getImpactColor(impact?.impact_level || "UNKNOWN");
  const badgeVariant = getBadgeVariant(impact?.impact_level || "UNKNOWN");
  const impactIcon = getImpactIcon(impact?.impact_level || "UNKNOWN");

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {impactIcon}
          Potential Societal Impact
        </CardTitle>
        <CardDescription>
          Assessment of potential societal harm if content is misinformation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Impact Level Badge */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Impact Level:</span>
          <Badge variant={badgeVariant} className="flex items-center gap-1">
            {impact?.impact_level}
          </Badge>
        </div>

        {/* Impact Score */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Impact Score:</span>
            <span className={`font-mono text-sm ${impactColor}`}>
              {((impact?.impact_score || 0) * 100).toFixed(1)}%
            </span>
          </div>
          
          {/* Visual Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                impact?.impact_level === "HIGH"
                  ? "bg-red-500"
                  : impact?.impact_level === "MEDIUM"
                  ? "bg-yellow-500"
                  : "bg-green-500"
              }`}
              style={{ width: `${(impact?.impact_score || 0) * 100}%` }}
            />
          </div>
        </div>

        {/* Explanation */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-gray-900">Explanation:</h4>
          <p className="text-sm text-gray-700 leading-relaxed">
            {impact?.impact_explanation || "No explanation available"}
          </p>
        </div>

        {/* Recommended Action */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-gray-900">Recommended Action:</h4>
          <div className={`p-3 rounded-md text-sm ${
            impact?.impact_level === "HIGH"
              ? "bg-red-50 border border-red-200 text-red-800"
              : impact?.impact_level === "MEDIUM"
              ? "bg-yellow-50 border border-yellow-200 text-yellow-800"
              : "bg-green-50 border border-green-200 text-green-800"
          }`}>
            <div className="flex items-start gap-2">
              <Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{impact?.recommended_action || "No action recommended"}</span>
            </div>
          </div>
        </div>

        {/* Additional Metadata */}
        {impact?.impact_level !== "UNKNOWN" && (
          <div className="text-xs text-gray-500 border-t pt-3">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Assessment based on:</span>
                <span>Keyword analysis & content classification</span>
              </div>
              <div className="flex justify-between">
                <span>Impact categories:</span>
                <span>
                  {impact?.impact_level === "HIGH" && "Safety & Security"}
                  {impact?.impact_level === "MEDIUM" && "Health & Economy"}
                  {impact?.impact_level === "LOW" && "General Information"}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
