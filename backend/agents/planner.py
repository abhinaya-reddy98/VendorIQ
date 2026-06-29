import time
from typing import List, Optional
from models.schemas import AnalysisResult, AgentStep, VendorInfo
from agents.document_agent import run_document_agent
from agents.policy_agent import run_policy_agent
from agents.compliance_agent import run_compliance_agent
from agents.risk_agent import run_risk_agent
from agents.decision_agent import run_decision_agent
from agents.memory_agent import store_analysis
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_planner_agent(
    file_paths: List[str] = None,
    what_if_scenario: Optional[str] = None,
    existing_vendor_info: Optional[VendorInfo] = None,
    persist_memory: bool = True,
) -> AnalysisResult:
    """
    Planner Agent: orchestrates the complete vendor onboarding analysis workflow.
    Coordinates all specialist agents in sequence and returns the full result.
    """
    timeline: List[AgentStep] = []
    overall_start = time.time()

    logger.info("=" * 60)
    logger.info(
        f"Planner Agent: starting analysis for {len(file_paths or [])} document(s)"
    )
    logger.info("=" * 60)

    # Step 1: Planner init
    planner_step = AgentStep(
        agent="Planner",
        status="completed",
        output={
            "files": len(file_paths or []),
            "what_if": bool(what_if_scenario),
            "vendor_info_override": bool(existing_vendor_info),
        },
        duration_ms=5,
    )
    timeline.append(planner_step)

    # Step 2: Document Analysis or use existing vendor info
    if existing_vendor_info is not None:
        logger.info("→ Step 2: Document Analysis Agent (skipped - vendor info supplied)")
        vendor_info = existing_vendor_info
        doc_step = AgentStep(
            agent="Document Analysis",
            status="skipped",
            output={"reason": "Vendor info supplied directly for what-if analysis"},
            duration_ms=0,
        )
        timeline.append(doc_step)
    else:
        logger.info("→ Step 2: Document Analysis Agent")
        vendor_info, doc_step = run_document_agent(file_paths or [])
        timeline.append(doc_step)

    # Step 3: Policy Retrieval
    logger.info("→ Step 3: Policy RAG Agent")
    policies, policy_excerpts, policy_step = run_policy_agent(vendor_info.model_dump())
    timeline.append(policy_step)

    # Step 4: Compliance Check
    logger.info("→ Step 4: Compliance Agent")
    compliance, compliance_step = run_compliance_agent(vendor_info, policies)
    timeline.append(compliance_step)

    # Step 5: Risk Assessment
    logger.info("→ Step 5: Risk Assessment Agent")
    risk, risk_step = run_risk_agent(compliance)
    timeline.append(risk_step)

    # Step 6: Decision
    logger.info("→ Step 6: Decision Agent (Gemini)")
    decision, decision_step = run_decision_agent(
        vendor_info, compliance, risk, policies, what_if_scenario
    )
    timeline.append(decision_step)

    # Assemble full result
    result = AnalysisResult(
        vendor_info=vendor_info,
        compliance=compliance,
        risk=risk,
        decision=decision,
        policy_excerpts=policy_excerpts,
        agent_timeline=timeline,
    )

    # Step 7: Memory (async store)
    if persist_memory:
        logger.info("→ Step 7: Memory Agent")
        await store_analysis(result)
    else:
        logger.info("→ Step 7: Memory Agent skipped (what-if simulation)")

    total_ms = int((time.time() - overall_start) * 1000)
    logger.info(f"Planner Agent: analysis complete in {total_ms}ms")
    logger.info(f"  → Recommendation: {decision.recommendation.value}")
    logger.info(f"  → Risk Level: {risk.risk_level.value}")
    logger.info(f"  → Compliance Score: {compliance.compliance_score}%")
    logger.info("=" * 60)

    return result
