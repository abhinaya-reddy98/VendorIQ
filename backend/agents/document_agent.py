import fitz  # PyMuPDF
import re
import json
import time
from typing import List, Dict, Any
from models.schemas import VendorInfo, AgentStep
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdfs(file_paths: List[str]) -> str:
    """Extract all text from multiple PDF files."""
    combined_text = ""
    for path in file_paths:
        try:
            doc = fitz.open(path)
            for page in doc:
                combined_text += page.get_text() + "\n"
            doc.close()
            logger.info(f"Extracted text from: {path}")
        except Exception as e:
            logger.error(f"Failed to read PDF {path}: {e}")
    return combined_text


def parse_vendor_info(text: str) -> VendorInfo:
    """Parse structured vendor information from raw text using regex patterns."""
    info = VendorInfo(raw_text=text[:2000])

    # Company name patterns
    company_patterns = [
        r"(?:Company\s*Name|Business\s*Name|Vendor\s*Name|Firm\s*Name)[:\s]+([A-Z][^\n,]{3,60}(?:Ltd|Pvt|LLP|Inc|Corp|Limited|Private)?)",
        r"^([A-Z][A-Za-z\s]+(?:Ltd|Pvt|LLP|Inc|Corp|Limited|Private)\b[.]?)",
        r"(?:Registered\s*as|Trading\s*as)[:\s]+([A-Z][^\n]{5,60})",
    ]
    for pattern in company_patterns:
        m = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if m:
            info.company_name = m.group(1).strip()
            break
    if not info.company_name:
        # fallback: grab first capitalized multi-word string
        m = re.search(r"([A-Z][a-z]+(?: [A-Z][a-z]+){1,4}(?:\s+(?:Pvt|Ltd|LLP|Inc|Corp))?\.?)", text)
        if m:
            info.company_name = m.group(1).strip()

    # GST Number: 15-character alphanumeric
    gst_m = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b", text)
    if gst_m:
        info.gst_number = gst_m.group(1)

    # PAN Number: AAAAA9999A format
    pan_m = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b", text)
    if pan_m:
        info.pan_number = pan_m.group(1)

    # ISO Certificate Expiry
    iso_patterns = [
        r"(?:ISO\s*(?:Certificate)?\s*(?:Expiry|Valid\s*Until|Expiration)\s*(?:Date)?)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"(?:Valid\s*Till|Validity)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"(?:Expiry\s*Date|Expiration|Valid\s*Until)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"(?:Valid\s*From[:\s]+[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}\s*\n.*?Valid\s*Until[:\s]+)([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"Valid\s+Until\s*\(Expiry\s+Date\)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
    ]
    for pattern in iso_patterns:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            info.iso_certificate_expiry = m.group(1)
            break

    # Bank details
    bank_m = re.search(r"(?:Bank\s*Name|Bank)[:\s]+([A-Z][A-Za-z\s]+Bank(?:\s+of\s+[A-Za-z]+)?)", text, re.IGNORECASE)
    if bank_m:
        info.bank_name = bank_m.group(1).strip()

    acc_m = re.search(r"(?:Account\s*(?:Number|No\.?)|A/C\s*No\.?)[:\s]+([0-9]{9,18})", text, re.IGNORECASE)
    if acc_m:
        info.account_number = acc_m.group(1)

    ifsc_m = re.search(r"(?:IFSC\s*(?:Code)?)[:\s]+([A-Z]{4}0[A-Z0-9]{6})", text, re.IGNORECASE)
    if ifsc_m:
        info.ifsc_code = ifsc_m.group(1)

    # Audit Score
    audit_patterns = [
        r"(?:Audit\s*Score|Overall\s*Score|Total\s*Score|Final\s*Score)[:\s]+([0-9]{1,3}(?:\.[0-9]+)?)\s*(?:/\s*100)?",
        r"([0-9]{1,3}(?:\.[0-9]+)?)\s*/\s*100\s*(?:audit|score)",
    ]
    for pattern in audit_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            score = float(m.group(1))
            if 0 <= score <= 100:
                info.audit_score = score
                break

    # Registration details
    reg_m = re.search(
        r"(?:Registration\s*(?:Number|No\.?)|Reg\.\s*No\.?|CIN|Corporate\s*Identification\s*Number)[:\s]+([A-Z0-9]{8,25})",
        text, re.IGNORECASE
    )
    if not reg_m:
        # Also match U28910MH2015PTC267543 style CIN at start of a value
        reg_m = re.search(r"\b([A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})\b", text)
    if reg_m:
        info.registration_number = reg_m.group(1)

    reg_date_m = re.search(r"(?:Date\s*of\s*(?:Incorporation|Registration)|Registered\s*on)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})", text, re.IGNORECASE)
    if reg_date_m:
        info.registration_date = reg_date_m.group(1)

    # Email
    email_m = re.search(r"\b([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})\b", text)
    if email_m:
        info.contact_email = email_m.group(1)

    # Address (simple heuristic)
    addr_m = re.search(r"(?:Address|Registered\s*Office)[:\s]+([^\n]{20,120})", text, re.IGNORECASE)
    if addr_m:
        info.address = addr_m.group(1).strip()

    return info


def run_document_agent(file_paths: List[str]) -> tuple[VendorInfo, AgentStep]:
    """Run the document analysis agent and return structured vendor info."""
    start = time.time()
    logger.info(f"Document Agent: processing {len(file_paths)} files")

    raw_text = extract_text_from_pdfs(file_paths)
    vendor_info = parse_vendor_info(raw_text)

    duration = int((time.time() - start) * 1000)
    step = AgentStep(
        agent="Document Analysis",
        status="completed",
        output={
            "company_name": vendor_info.company_name,
            "gst_number": vendor_info.gst_number,
            "pan_number": vendor_info.pan_number,
            "iso_expiry": vendor_info.iso_certificate_expiry,
            "audit_score": vendor_info.audit_score,
            "bank_name": vendor_info.bank_name,
            "registration_number": vendor_info.registration_number,
        },
        duration_ms=duration,
    )
    return vendor_info, step
