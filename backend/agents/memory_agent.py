import time
from datetime import datetime
from models.schemas import AnalysisResult, ApproveRequest, VendorHistoryRecord, AgentStep
from database.mongo import get_db
from utils.logger import get_logger
from typing import List, Optional
from bson import ObjectId

logger = get_logger(__name__)


async def store_analysis(analysis: AnalysisResult) -> str:
    """Store full analysis result in MongoDB."""
    db = get_db()
    doc = {
        "vendor_name": analysis.vendor_info.company_name,
        "gst_number": analysis.vendor_info.gst_number,
        "pan_number": analysis.vendor_info.pan_number,
        "recommendation": analysis.decision.recommendation.value,
        "confidence_score": analysis.decision.confidence_score,
        "risk_level": analysis.risk.risk_level.value,
        "compliance_score": analysis.compliance.compliance_score,
        "violations": analysis.compliance.violations,
        "missing_documents": analysis.compliance.missing_documents,
        "reason": analysis.decision.reason,
        "next_best_action": analysis.decision.next_best_action,
        "processed_at": analysis.processed_at,
        "human_decision": None,
        "human_notes": None,
        "human_reviewed_at": None,
    }
    try:
        result = await db["vendor_analyses"].insert_one(doc)
        logger.info(f"Memory Agent: stored analysis for {doc['vendor_name']} -> {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Memory Agent: failed to store analysis: {e}")
        return ""


async def store_human_decision(request: ApproveRequest) -> bool:
    """Record human approval/rejection decision."""
    db = get_db()
    doc = {
        "vendor_name": request.vendor_name,
        "recommendation": request.recommendation,
        "human_decision": request.human_decision.value,
        "notes": request.notes,
        "confidence_score": request.confidence_score,
        "risk_level": request.risk_level,
        "compliance_score": request.compliance_score,
        "timestamp": datetime.utcnow(),
    }
    try:
        await db["vendor_decisions"].insert_one(doc)
        # Also update the analysis record if it exists
        await db["vendor_analyses"].update_one(
            {"vendor_name": request.vendor_name},
            {
                "$set": {
                    "human_decision": request.human_decision.value,
                    "human_notes": request.notes,
                    "human_reviewed_at": datetime.utcnow(),
                }
            },
            sort=[("processed_at", -1)],
        )
        logger.info(f"Memory Agent: human decision '{request.human_decision.value}' stored for {request.vendor_name}")
        return True
    except Exception as e:
        logger.error(f"Memory Agent: failed to store human decision: {e}")
        return False


async def get_vendor_history(limit: int = 50) -> List[dict]:
    """Retrieve vendor decision history from MongoDB."""
    db = get_db()
    try:
        cursor = db["vendor_decisions"].find({}).sort("timestamp", -1).limit(limit)
        records = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            records.append(doc)
        logger.info(f"Memory Agent: retrieved {len(records)} history records")
        return records
    except Exception as e:
        logger.error(f"Memory Agent: failed to retrieve history: {e}")
        return []
