import os
import uuid
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
from agents.planner import run_planner_agent
from models.schemas import AnalysisResult, WhatIfRequest
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload", response_model=AnalysisResult)
async def upload_vendor_documents(
    files: List[UploadFile] = File(...),
    what_if_scenario: Optional[str] = Form(None),
):
    """
    Accept vendor PDF documents and run the full agentic analysis pipeline.
    Returns a complete recommendation with compliance checklist, risk assessment, and AI decision.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Validate file types
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are accepted. Got: {f.filename}",
            )

    # Save uploaded files to temp directory
    temp_dir = tempfile.mkdtemp()
    file_paths = []

    try:
        for upload in files:
            safe_name = f"{uuid.uuid4().hex}_{upload.filename}"
            temp_path = os.path.join(temp_dir, safe_name)
            content = await upload.read()
            with open(temp_path, "wb") as f:
                f.write(content)
            file_paths.append(temp_path)
            logger.info(f"Saved uploaded file: {upload.filename} -> {temp_path}")

        # Run the agentic pipeline
        result = await run_planner_agent(file_paths, what_if_scenario)
        return result

    except Exception as e:
        logger.error(f"Upload processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp files
        for path in file_paths:
            try:
                os.remove(path)
            except Exception:
                pass
        try:
            os.rmdir(temp_dir)
        except Exception:
            pass


@router.post("/whatif")
async def what_if_analysis(request: WhatIfRequest):
    """
    Re-run analysis with a what-if scenario modification.
    """
    if request.vendor_info is None:
        raise HTTPException(
            status_code=400,
            detail="Vendor info is required for what-if analysis.",
        )

    try:
        result = await run_planner_agent(
            file_paths=[],
            what_if_scenario=f"Current vendor: {request.vendor_name}. Scenario: {request.scenario}",
            existing_vendor_info=request.vendor_info,
            persist_memory=False,
        )
        return {
            "original_recommendation": request.current_analysis.get("recommendation"),
            "what_if_recommendation": result.decision.recommendation.value,
            "what_if_analysis": result.decision.what_if_analysis,
            "confidence_delta": result.decision.confidence_score,
            "reason": result.decision.reason,
        }
    except Exception as e:
        logger.error(f"What-if analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
