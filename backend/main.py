from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.upload import router as upload_router
from api.vendor import router as vendor_router
from database.mongo import close_db
from rag.chroma_store import get_chroma_collection
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, clean up on shutdown."""
    logger.info("VendorIQ API starting up...")
    try:
        get_chroma_collection()
        logger.info("ChromaDB initialized with procurement policies")
    except Exception as e:
        logger.warning(f"ChromaDB init warning: {e}")

    yield

    logger.info("VendorIQ API shutting down...")
    await close_db()


app = FastAPI(
    title="VendorIQ – Agentic Vendor Intelligence API",
    description="AI-powered vendor onboarding and risk assessment platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, tags=["Analysis"])
app.include_router(vendor_router, tags=["Vendor Management"])


@app.get("/")
async def root():
    return {
        "name": "VendorIQ API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }
