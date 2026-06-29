import time
import json
import re
from typing import List
from models.schemas import (
    VendorInfo,
    ComplianceResult,
    RiskResult,
    DecisionResult,
    Recommendation,
    AgentStep,
)
from config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


def _build_decision_prompt(
    vendor_info: VendorInfo,
    compliance: ComplianceResult,
    risk: RiskResult,
    policies: List[dict],
    what_if_scenario: str = None,
) -> str:
    policy_text = "\n".join(
        [f"- {p['title']}: {p['content'][:300]}" for p in policies[:5]]
    )

    compliance_summary = "\n".join(
        [
            f"  {'✓' if c.status else '✗'} {c.check}: {c.detail}"
            for c in compliance.checklist
        ]
    )

    what_if_section = ""
    if what_if_scenario:
        what_if_section = f"\n\nWHAT-IF SCENARIO TO EVALUATE:\n{what_if_scenario}\n"

    return f"""You are an expert procurement risk analyst AI. Analyze this vendor onboarding request and provide a structured decision.

VENDOR INFORMATION:
- Company: {vendor_info.company_name or 'Unknown'}
- GST: {vendor_info.gst_number or 'Not provided'}
- PAN: {vendor_info.pan_number or 'Not provided'}
- ISO Expiry: {vendor_info.iso_certificate_expiry or 'Not provided'}
- Audit Score: {vendor_info.audit_score or 'Not provided'}
- Bank: {vendor_info.bank_name or 'Not provided'}
- Registration: {vendor_info.registration_number or 'Not provided'}

COMPLIANCE RESULTS:
{compliance_summary}
- Overall Compliance Score: {compliance.compliance_score}%
- Violations: {len(compliance.violations)}
- Missing Documents: {', '.join(compliance.missing_documents) if compliance.missing_documents else 'None'}

RISK ASSESSMENT:
- Risk Level: {risk.risk_level.value}
- Failure Count: {risk.failure_count}

APPLICABLE POLICIES:
{policy_text}
{what_if_section}
Based on this analysis, provide your decision in the following JSON format ONLY (no other text):
{{
  "recommendation": "<one of: Approve Vendor | Reject Vendor | Request Missing Documents | Escalate for Manual Review>",
  "reason": "<2-3 sentence explanation of the recommendation>",
  "confidence_score": <float between 0.0 and 1.0>,
  "supporting_policy": "<the most relevant policy title and key requirement>",
  "evidence": ["<evidence point 1>", "<evidence point 2>", "<evidence point 3>"],
  "next_best_action": "<specific actionable next step for the procurement team>",
  "what_if_analysis": "<only if what-if scenario provided: how the new scenario changes the recommendation>"
}}

STRICT DECISION RULES — follow these exactly in priority order:

RULE 1 — "Request Missing Documents": Use this if missing_documents list is NOT empty OR any compliance check failed due to missing info. This takes priority over Escalate whenever docs are simply absent.

RULE 2 — "Approve Vendor": Use this if compliance_score >= 90% AND risk=Low AND violations=0.

RULE 3 — "Reject Vendor": Use this if failure_count >= 4 AND compliance_score < 30% AND risk=High.

RULE 4 — "Escalate for Manual Review": Use ONLY when none of the above rules apply — borderline cases where docs are present but quality is questionable.

Confidence rules:
- "Approve Vendor" with 100% compliance → confidence 0.90-0.99
- "Request Missing Documents" → confidence 0.80-0.90 (clear-cut)
- "Reject Vendor" → confidence 0.70-0.85
- "Escalate for Manual Review" → confidence 0.55-0.70

IMPORTANT: If missing_documents is not empty, you MUST return "Request Missing Documents". Do not return "Escalate for Manual Review" when documents are simply missing.
"""


def _parse_gemini_response(text: str) -> dict:
    """Extract JSON from Gemini's response."""
    # Try to find JSON block
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback structure
    return {
        "recommendation": "Escalate for Manual Review",
        "reason": "Automated analysis inconclusive. Human review required for final determination.",
        "confidence_score": 0.5,
        "supporting_policy": "Risk Classification Framework",
        "evidence": ["Automated parsing failed", "Manual review recommended"],
        "next_best_action": "Escalate to senior procurement analyst for manual review",
        "what_if_analysis": None,
    }


def run_decision_agent(
    vendor_info: VendorInfo,
    compliance: ComplianceResult,
    risk: RiskResult,
    policies: List[dict],
    what_if_scenario: str = None,
) -> tuple[DecisionResult, AgentStep]:
    """Use Gemini 2.5 Flash to generate a final vendor recommendation."""
    start = time.time()
    logger.info("Decision Agent: generating recommendation with Gemini")

    settings = get_settings()
    prompt = _build_decision_prompt(vendor_info, compliance, risk, policies, what_if_scenario)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1024,
            ),
        )
        raw_text = response.text
        logger.info("Gemini response received")
        parsed = _parse_gemini_response(raw_text)

    except Exception as e:
        logger.error(f"Gemini API error: {e}. Using rule-based fallback.")
        parsed = _rule_based_fallback(compliance, risk)

    # Validate recommendation enum
    valid_recommendations = {r.value for r in Recommendation}
    rec_value = parsed.get("recommendation", "Escalate for Manual Review")
    if rec_value not in valid_recommendations:
        rec_value = "Escalate for Manual Review"

    result = DecisionResult(
        recommendation=Recommendation(rec_value),
        reason=parsed.get("reason", ""),
        confidence_score=float(parsed.get("confidence_score", 0.5)),
        supporting_policy=parsed.get("supporting_policy", ""),
        evidence=parsed.get("evidence", []),
        next_best_action=parsed.get("next_best_action", ""),
        what_if_analysis=parsed.get("what_if_analysis"),
    )

    duration = int((time.time() - start) * 1000)
    step = AgentStep(
        agent="Decision",
        status="completed",
        output={
            "recommendation": result.recommendation.value,
            "confidence_score": result.confidence_score,
            "risk_level": risk.risk_level.value,
        },
        duration_ms=duration,
    )

    logger.info(f"Decision Agent: {result.recommendation.value} (confidence={result.confidence_score})")
    return result, step


def _rule_based_fallback(compliance: ComplianceResult, risk: RiskResult) -> dict:
    """Fallback when Gemini is unavailable."""
    if compliance.compliance_score >= 90 and risk.failure_count == 0:
        return {
            "recommendation": "Approve Vendor",
            "reason": "Vendor meets all mandatory compliance requirements with zero violations. Risk level is low.",
            "confidence_score": 0.88,
            "supporting_policy": "Risk Classification Framework: Low Risk vendors can be approved",
            "evidence": [
                f"Compliance score: {compliance.compliance_score}%",
                "Zero policy violations",
                f"Risk level: {risk.risk_level.value}",
            ],
            "next_best_action": "Proceed with vendor contract finalization and onboarding",
            "what_if_analysis": None,
        }
    elif compliance.missing_documents:
        return {
            "recommendation": "Request Missing Documents",
            "reason": f"Vendor submission is incomplete. {len(compliance.missing_documents)} document(s) are missing.",
            "confidence_score": 0.82,
            "supporting_policy": "Document Completeness Policy: minimum 5 mandatory documents required",
            "evidence": [
                f"Missing: {', '.join(compliance.missing_documents)}",
                f"Compliance score: {compliance.compliance_score}%",
                f"Violations: {len(compliance.violations)}",
            ],
            "next_best_action": f"Request the following documents from vendor: {', '.join(compliance.missing_documents)}",
            "what_if_analysis": None,
        }
    elif risk.failure_count >= 2:
        return {
            "recommendation": "Reject Vendor",
            "reason": f"Vendor has {risk.failure_count} critical compliance failures. High risk classification warrants rejection.",
            "confidence_score": 0.75,
            "supporting_policy": "Risk Classification Framework: High Risk requires CFO and CISO approval",
            "evidence": compliance.violations[:3],
            "next_best_action": "Notify vendor of rejection and list remediation requirements for re-application",
            "what_if_analysis": None,
        }
    else:
        return {
            "recommendation": "Escalate for Manual Review",
            "reason": "Vendor has borderline compliance metrics. Senior procurement officer review required.",
            "confidence_score": 0.6,
            "supporting_policy": "Risk Classification Framework: Medium Risk requires department head approval",
            "evidence": [
                f"Compliance score: {compliance.compliance_score}%",
                f"Risk level: {risk.risk_level.value}",
                f"Violations: {len(compliance.violations)}",
            ],
            "next_best_action": "Route to department head for final review within 48 hours",
            "what_if_analysis": None,
        }