from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Recommendation(str, Enum):
    APPROVE = "Approve Vendor"
    REJECT = "Reject Vendor"
    REQUEST_DOCS = "Request Missing Documents"
    ESCALATE = "Escalate for Manual Review"


class HumanDecision(str, Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    DEFERRED = "Deferred"


class VendorInfo(BaseModel):
    company_name: str = ""
    gst_number: str = ""
    pan_number: str = ""
    iso_certificate_expiry: str = ""
    bank_name: str = ""
    account_number: str = ""
    ifsc_code: str = ""
    audit_score: Optional[float] = None
    registration_number: str = ""
    registration_date: str = ""
    contact_email: str = ""
    address: str = ""
    raw_text: str = ""


class ComplianceItem(BaseModel):
    check: str
    status: bool
    detail: str
    policy_reference: str = ""


class ComplianceResult(BaseModel):
    checklist: List[ComplianceItem]
    violations: List[str]
    missing_documents: List[str]
    compliance_score: float


class RiskResult(BaseModel):
    risk_level: RiskLevel
    reasons: List[str]
    failure_count: int


class DecisionResult(BaseModel):
    recommendation: Recommendation
    reason: str
    confidence_score: float
    supporting_policy: str
    evidence: List[str]
    next_best_action: str
    what_if_analysis: Optional[str] = None


class AgentStep(BaseModel):
    agent: str
    status: str
    output: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None


class AnalysisResult(BaseModel):
    vendor_info: VendorInfo
    compliance: ComplianceResult
    risk: RiskResult
    decision: DecisionResult
    policy_excerpts: List[str]
    agent_timeline: List[AgentStep]
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class ApproveRequest(BaseModel):
    vendor_name: str
    recommendation: str
    human_decision: HumanDecision
    notes: Optional[str] = ""
    confidence_score: float
    risk_level: str
    compliance_score: float


class VendorHistoryRecord(BaseModel):
    id: Optional[str] = None
    vendor_name: str
    recommendation: str
    human_decision: Optional[str] = None
    confidence_score: float
    risk_level: str
    compliance_score: float
    notes: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WhatIfRequest(BaseModel):
    vendor_name: str
    scenario: str
    current_analysis: Dict[str, Any]
    vendor_info: Optional[VendorInfo] = None
