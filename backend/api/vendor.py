from fastapi import APIRouter, HTTPException
from models.schemas import ApproveRequest
from agents.memory_agent import store_human_decision, get_vendor_history
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/approve")
async def approve_vendor(request: ApproveRequest):
    """
    Record a human procurement officer's approval or rejection decision.
    Stores the decision in MongoDB alongside the AI recommendation.
    """
    try:
        success = await store_human_decision(request)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store decision")
        logger.info(f"Human decision recorded: {request.human_decision} for {request.vendor_name}")
        return {
            "status": "success",
            "message": f"Decision '{request.human_decision}' recorded for vendor '{request.vendor_name}'",
            "vendor_name": request.vendor_name,
            "human_decision": request.human_decision,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approve endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(limit: int = 50):
    """
    Retrieve the full vendor onboarding decision history from MongoDB.
    """
    try:
        records = await get_vendor_history(limit=limit)
        return {
            "total": len(records),
            "records": records,
        }
    except Exception as e:
        logger.error(f"History endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VendorIQ API", "version": "1.0.0"}
