from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class SecurityVulnerability(BaseModel):
    """
    Standardized schema for security vulnerabilities from any source 
    (ESLint, Snyk, ZAP, SonarQube).
    """
    source: str = Field(..., description="The tool that identified the vulnerability (e.g., 'eslint', 'snyk')")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM)
    rule_id: str = Field(..., description="The specific tool rule or CVE ID")
    description: str = Field(..., description="Clear explanation of the finding")
    file_path: Optional[str] = Field(None, description="Path to the affected file")
    line_number: Optional[int] = Field(None, description="Line number where the issue occurs")
    remediation: Optional[str] = Field(None, description="Suggested fix or mitigation steps")
    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Original tool output for deeper inspection")
    identified_at: datetime = Field(default_factory=datetime.utcnow)

class SecurityPostureSummary(BaseModel):
    """Aggregated view of security health across tools."""
    total_findings: int
    counts_by_severity: Dict[SeverityLevel, int]
    counts_by_source: Dict[str, int]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
