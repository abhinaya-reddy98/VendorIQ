import chromadb
from chromadb.utils import embedding_functions
from config import get_settings
from utils.logger import get_logger
from typing import List

logger = get_logger(__name__)

PROCUREMENT_POLICIES = [
    {
        "id": "pol_001",
        "title": "GST Registration Requirement",
        "content": "All vendors must provide a valid GST (Goods and Services Tax) registration certificate. The GST number must be active and verifiable. Vendors without a valid GST registration will be automatically rejected. GST certificate must be dated within the last 3 years.",
        "category": "compliance",
        "severity": "mandatory",
    },
    {
        "id": "pol_002",
        "title": "PAN Card Requirement",
        "content": "Every vendor entity must submit a valid Permanent Account Number (PAN) card issued by the Income Tax Department of India. The PAN must match the company name on the registration documents. Individual proprietors must provide personal PAN.",
        "category": "compliance",
        "severity": "mandatory",
    },
    {
        "id": "pol_003",
        "title": "ISO Certification Policy",
        "content": "Vendors providing manufacturing or quality-sensitive services must hold a valid ISO 9001:2015 certification or equivalent. ISO certificates must be current and not expired. Certificates expiring within 90 days require renewal confirmation. Expired ISO certificates constitute a compliance failure.",
        "category": "quality",
        "severity": "mandatory",
    },
    {
        "id": "pol_004",
        "title": "Factory Audit Score Threshold",
        "content": "All manufacturing vendors must achieve a minimum factory audit score of 80 out of 100. Vendors scoring between 70-79 may be conditionally approved with a 6-month improvement plan. Vendors scoring below 70 are ineligible for vendor approval and must reapply after remediation.",
        "category": "quality",
        "severity": "mandatory",
    },
    {
        "id": "pol_005",
        "title": "Bank Account Verification",
        "content": "Vendors must provide valid bank account details including account number, IFSC code, and bank name. Bank details must be in the company name and match registration documents. Cancelled cheque or bank statement must be provided for verification. Personal accounts are not acceptable for vendor payments.",
        "category": "financial",
        "severity": "mandatory",
    },
    {
        "id": "pol_006",
        "title": "Company Registration Certificate",
        "content": "Vendors must submit a valid company registration certificate from the Registrar of Companies (ROC) or equivalent authority. The certificate must show company name, registration number, and date of incorporation. Companies less than 2 years old require additional financial due diligence.",
        "category": "legal",
        "severity": "mandatory",
    },
    {
        "id": "pol_007",
        "title": "Security Compliance Assessment",
        "content": "Vendors handling sensitive data must complete the VendorIQ Security Questionnaire. Data handling vendors must comply with ISO 27001 or SOC 2 standards. Security assessments scoring below 70% indicate high risk. All security questionnaire responses must be verified by the security team before approval.",
        "category": "security",
        "severity": "high",
    },
    {
        "id": "pol_008",
        "title": "Risk Classification Framework",
        "content": "Vendor risk is classified as: Low Risk (0 compliance failures, audit score ≥ 90), Medium Risk (1 compliance failure or audit score 80-89), High Risk (2 or more failures or audit score below 80). High-risk vendors require CISO and CFO approval. Medium-risk vendors require department head approval.",
        "category": "risk",
        "severity": "framework",
    },
    {
        "id": "pol_009",
        "title": "Document Completeness Policy",
        "content": "Vendor onboarding requires a minimum of 5 mandatory documents: GST certificate, PAN card, bank details, company registration, and ISO certificate (if applicable). Incomplete submissions will be returned with a document request notice. Vendors have 14 days to complete their submission before re-evaluation is required.",
        "category": "process",
        "severity": "standard",
    },
    {
        "id": "pol_010",
        "title": "Conflict of Interest Declaration",
        "content": "Vendors must disclose any existing relationships with company employees or board members. Undisclosed conflicts of interest result in immediate rejection and potential blacklisting. Disclosed relationships are reviewed by the ethics committee before onboarding approval.",
        "category": "ethics",
        "severity": "mandatory",
    },
]

_chroma_client = None
_collection = None


def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection

    settings = get_settings()
    try:
        _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        _collection = _chroma_client.get_or_create_collection(
            name="procurement_policies",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        if _collection.count() == 0:
            logger.info("Seeding ChromaDB with procurement policies...")
            _collection.add(
                ids=[p["id"] for p in PROCUREMENT_POLICIES],
                documents=[p["content"] for p in PROCUREMENT_POLICIES],
                metadatas=[
                    {
                        "title": p["title"],
                        "category": p["category"],
                        "severity": p["severity"],
                    }
                    for p in PROCUREMENT_POLICIES
                ],
            )
            logger.info(f"Seeded {len(PROCUREMENT_POLICIES)} policies into ChromaDB")
        else:
            logger.info(
                f"ChromaDB already has {_collection.count()} policies loaded"
            )

    except Exception as e:
        logger.error(f"ChromaDB initialization error: {e}")
        raise

    return _collection


def retrieve_policies(query: str, n_results: int = 3) -> List[dict]:
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )
    policies = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            policies.append(
                {
                    "content": doc,
                    "title": results["metadatas"][0][i].get("title", ""),
                    "category": results["metadatas"][0][i].get("category", ""),
                    "severity": results["metadatas"][0][i].get("severity", ""),
                    "distance": results["distances"][0][i]
                    if results.get("distances")
                    else 0,
                }
            )
    return policies
