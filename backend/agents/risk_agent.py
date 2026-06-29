import time
from models.schemas import ComplianceResult, RiskResult, RiskLevel, AgentStep
from utils.logger import get_logger

logger = get_logger(__name__)


def run_risk_agent(compliance: ComplianceResult) -> tuple[RiskResult, AgentStep]:
    """Assess vendor risk based on compliance failures."""
    start = time.time()
    logger.info("Risk Agent: assessing vendor risk level")

    failure_count = len(compliance.violations)
    reasons = []

    # Core risk logic
    if failure_count == 0:
        risk_level = RiskLevel.LOW
        reasons.append("All mandatory compliance checks passed")
        reasons.append("No policy violations detected")
        if compliance.compliance_score == 100:
            reasons.append("Perfect compliance score achieved")
    elif failure_count == 1:
        risk_level = RiskLevel.MEDIUM
        reasons.append(f"1 compliance failure detected: {compliance.violations[0]}")
        reasons.append("Vendor can proceed with corrective action plan")
    else:
        risk_level = RiskLevel.HIGH
        reasons.append(f"{failure_count} compliance failures detected")
        for v in compliance.violations[:3]:
            reasons.append(f"• {v}")
        if failure_count > 3:
            reasons.append(f"• ...and {failure_count - 3} more violations")
        reasons.append("Requires CISO and CFO approval before proceeding")

    # Additional risk signals
    if compliance.missing_documents:
        reasons.append(
            f"Missing documents: {', '.join(compliance.missing_documents[:3])}"
        )

    if compliance.compliance_score < 50:
        reasons.append("Critically low compliance score — immediate escalation recommended")

    result = RiskResult(
        risk_level=risk_level,
        reasons=reasons,
        failure_count=failure_count,
    )

    duration = int((time.time() - start) * 1000)
    step = AgentStep(
        agent="Risk Assessment",
        status="completed",
        output={
            "risk_level": risk_level.value,
            "failure_count": failure_count,
            "reasons": reasons,
        },
        duration_ms=duration,
    )

    logger.info(f"Risk Agent: {risk_level.value} risk ({failure_count} failures)")
    return result, step
