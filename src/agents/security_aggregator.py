import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agents.sub_agent import SubAgent
from src.storage.postgres_client import PostgresClient

logger = logging.getLogger(__name__)

class SecurityAggregatorAgent(SubAgent):
    """
    Agent responsible for aggregating security findings from multiple sources:
    - SARIF files (ESLint, ZAP)
    - Tool-specific JSON exports
    - Security tool APIs
    """
    
    def __init__(self):
        super().__init__("security-aggregator", domain="security")
        self.db = PostgresClient()
        self.db.connect()
    
    async def diagnose(self) -> Dict[str, Any]:
        """
        Scan for new security reports and ingest them.
        Identify the most critical security bottleneck.
        """
        logger.info("Running security aggregation scan...")
        
        # 1. Ingest ESLint SARIF if it exists
        sarif_path = "security-reports/eslint-results.sarif"
        findings_count = 0
        if os.path.exists(sarif_path):
            findings_count += self._ingest_sarif(sarif_path, source="eslint")
        
        # 2. Get summary for diagnosis
        summary = self.db.get_security_summary()
        
        if summary["total_findings"] > 0:
            # Determine bottleneck based on critical findings
            critical_count = summary["counts_by_severity"].get("critical", 0)
            high_count = summary["counts_by_severity"].get("high", 0)
            
            description = f"Found {summary['total_findings']} security vulnerabilities ({critical_count} critical, {high_count} high)."
            impact = min(10.0, (critical_count * 2.5) + (high_count * 1.5))
            
            return {
                "description": description,
                "confidence": 0.95,
                "impact_score": impact,
                "blocking": ["production deployment", "security compliance"],
                "recommended_action": "Review critical security findings in the Command Center dashboard."
            }
        
        return {
            "description": "No significant security vulnerabilities identified.",
            "confidence": 0.9,
            "impact_score": 0.0,
            "blocking": [],
            "recommended_action": "Continue regular security scans."
        }

    def _ingest_sarif(self, file_path: str, source: str) -> int:
        """Parse SARIF file and save vulnerabilities to DB"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            count = 0
            for run in data.get("runs", []):
                # Rules map
                rules = {}
                for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
                    rules[rule["id"]] = rule
                
                for result in run.get("results", []):
                    rule_id = result.get("ruleId")
                    rule = rules.get(rule_id, {})
                    
                    # Map severity
                    level = result.get("level", "warning")
                    severity = self._map_sarif_level(level)
                    
                    # Location
                    location = {}
                    if result.get("locations"):
                        loc = result["locations"][0].get("physicalLocation", {})
                        location["file"] = loc.get("artifactLocation", {}).get("uri")
                        location["line"] = loc.get("region", {}).get("startLine")
                    
                    vulnerability = {
                        "source": source,
                        "severity": severity,
                        "rule_id": rule_id,
                        "description": result.get("message", {}).get("text", "No description provided"),
                        "file_path": location.get("file"),
                        "line_number": location.get("line"),
                        "remediation": rule.get("helpUri", "Check tool documentation for remediation"),
                        "raw_data": result
                    }
                    
                    self.db.save_vulnerability(vulnerability)
                    count += 1
            
            logger.info(f"Ingested {count} findings from {file_path}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to ingest SARIF {file_path}: {e}")
            return 0

    def _map_sarif_level(self, level: str) -> str:
        mapping = {
            "error": "high",
            "warning": "medium",
            "note": "low",
            "none": "info"
        }
        return mapping.get(level, "medium")
