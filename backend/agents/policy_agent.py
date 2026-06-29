import time
from typing import List, Dict
from rag.chroma_store import retrieve_policies
from models.schemas import AgentStep
from utils.logger import get_logger

logger = get_logger(__name__)


def run_policy_agent(vendor_info_dict: dict) -> tuple[List[dict], List[str], AgentStep]:
    """Retrieve relevant policy sections from ChromaDB based on vendor context."""
    start = time.time()
    logger.info("Policy Agent: retrieving relevant policies from ChromaDB")

    queries = [
        "GST registration PAN card mandatory vendor compliance",
        "ISO certificate quality audit score threshold",
        "bank account financial verification vendor",
        "company registration legal documents",
        "risk classification vendor onboarding",
    ]

    seen_ids = set()
    all_policies = []

    for query in queries:
        results = retrieve_policies(query, n_results=2)
        for r in results:
            key = r["title"]
            if key not in seen_ids:
                seen_ids.add(key)
                all_policies.append(r)

    policy_excerpts = [
        f"[{p['title']}] {p['content'][:200]}..." for p in all_policies[:6]
    ]

    duration = int((time.time() - start) * 1000)
    step = AgentStep(
        agent="Policy Retrieval",
        status="completed",
        output={
            "policies_retrieved": len(all_policies),
            "top_policies": [p["title"] for p in all_policies[:4]],
        },
        duration_ms=duration,
    )

    logger.info(f"Policy Agent: retrieved {len(all_policies)} unique policies")
    return all_policies, policy_excerpts, step
