import time
from datetime import datetime, date
from typing import List
from models.schemas import VendorInfo, ComplianceItem, ComplianceResult, AgentStep
from utils.logger import get_logger

logger = get_logger(__name__)


def _parse_date(date_str: str):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def run_compliance_agent(
    vendor_info: VendorInfo, policies: List[dict]
) -> tuple[ComplianceResult, AgentStep]:
    """Compare vendor info against retrieved policies and generate compliance checklist."""
    start = time.time()
    logger.info("Compliance Agent: checking vendor against policies")

    checklist: List[ComplianceItem] = []
    violations: List[str] = []
    missing_docs: List[str] = []

    # 1. GST Check
    gst_ok = bool(vendor_info.gst_number and len(vendor_info.gst_number) == 15)
    checklist.append(
        ComplianceItem(
            check="GST Registration",
            status=gst_ok,
            detail=f"GST Number: {vendor_info.gst_number}" if gst_ok else "GST number missing or invalid",
            policy_reference="GST Registration Requirement (pol_001)",
        )
    )
    if not gst_ok:
        violations.append("Invalid or missing GST registration number")
        missing_docs.append("GST Certificate")

    # 2. PAN Check
    pan_ok = bool(vendor_info.pan_number and len(vendor_info.pan_number) == 10)
    checklist.append(
        ComplianceItem(
            check="PAN Card",
            status=pan_ok,
            detail=f"PAN Number: {vendor_info.pan_number}" if pan_ok else "PAN number missing or invalid",
            policy_reference="PAN Card Requirement (pol_002)",
        )
    )
    if not pan_ok:
        violations.append("Invalid or missing PAN card number")
        missing_docs.append("PAN Card")

    # 3. ISO Certificate Check
    iso_ok = False
    iso_detail = "ISO certificate information not found"
    if vendor_info.iso_certificate_expiry:
        expiry = _parse_date(vendor_info.iso_certificate_expiry)
        if expiry:
            today = date.today()
            days_remaining = (expiry - today).days
            if days_remaining > 0:
                iso_ok = True
                iso_detail = f"ISO certificate valid until {vendor_info.iso_certificate_expiry} ({days_remaining} days remaining)"
                if days_remaining < 90:
                    iso_detail += " — EXPIRING SOON (< 90 days)"
            else:
                iso_detail = f"ISO certificate EXPIRED on {vendor_info.iso_certificate_expiry}"
        else:
            iso_detail = f"ISO expiry date '{vendor_info.iso_certificate_expiry}' could not be parsed"
    checklist.append(
        ComplianceItem(
            check="ISO Certificate Validity",
            status=iso_ok,
            detail=iso_detail,
            policy_reference="ISO Certification Policy (pol_003)",
        )
    )
    if not iso_ok:
        violations.append("ISO certificate is expired, missing, or invalid")
        if not vendor_info.iso_certificate_expiry:
            missing_docs.append("ISO Certificate")

    # 4. Audit Score Check
    audit_ok = False
    audit_detail = "Factory audit report not found"
    if vendor_info.audit_score is not None:
        if vendor_info.audit_score >= 80:
            audit_ok = True
            audit_detail = f"Audit score: {vendor_info.audit_score}/100 (meets minimum threshold of 80)"
        elif vendor_info.audit_score >= 70:
            audit_detail = f"Audit score: {vendor_info.audit_score}/100 (below minimum 80; conditional approval possible)"
        else:
            audit_detail = f"Audit score: {vendor_info.audit_score}/100 (critically below minimum threshold of 80)"
    checklist.append(
        ComplianceItem(
            check="Factory Audit Score",
            status=audit_ok,
            detail=audit_detail,
            policy_reference="Factory Audit Score Threshold (pol_004)",
        )
    )
    if not audit_ok:
        violations.append(
            f"Factory audit score below required threshold (got {vendor_info.audit_score}, required ≥ 80)"
            if vendor_info.audit_score is not None
            else "Factory audit report missing"
        )
        if vendor_info.audit_score is None:
            missing_docs.append("Factory Audit Report")

    # 5. Bank Details Check
    bank_ok = bool(
        vendor_info.bank_name and vendor_info.account_number and vendor_info.ifsc_code
    )
    bank_detail = (
        f"Bank: {vendor_info.bank_name}, Account: ***{vendor_info.account_number[-4:] if vendor_info.account_number else ''}, IFSC: {vendor_info.ifsc_code}"
        if bank_ok
        else "Incomplete bank details (missing bank name, account number, or IFSC)"
    )
    checklist.append(
        ComplianceItem(
            check="Bank Account Verification",
            status=bank_ok,
            detail=bank_detail,
            policy_reference="Bank Account Verification (pol_005)",
        )
    )
    if not bank_ok:
        violations.append("Incomplete or missing bank account details")
        missing_docs.append("Bank Details / Cancelled Cheque")

    # 6. Company Registration Check
    reg_ok = bool(vendor_info.registration_number)
    checklist.append(
        ComplianceItem(
            check="Company Registration",
            status=reg_ok,
            detail=f"Registration No: {vendor_info.registration_number}" if reg_ok else "Company registration number not found",
            policy_reference="Company Registration Certificate (pol_006)",
        )
    )
    if not reg_ok:
        violations.append("Company registration certificate not found")
        missing_docs.append("Company Registration Certificate")

    # Compliance score
    passed = sum(1 for c in checklist if c.status)
    compliance_score = round((passed / len(checklist)) * 100, 1)

    result = ComplianceResult(
        checklist=checklist,
        violations=violations,
        missing_documents=list(set(missing_docs)),
        compliance_score=compliance_score,
    )

    duration = int((time.time() - start) * 1000)
    step = AgentStep(
        agent="Compliance Check",
        status="completed",
        output={
            "compliance_score": compliance_score,
            "passed_checks": passed,
            "total_checks": len(checklist),
            "violations": len(violations),
            "missing_documents": missing_docs,
        },
        duration_ms=duration,
    )

    logger.info(
        f"Compliance Agent: {passed}/{len(checklist)} checks passed, score={compliance_score}%"
    )
    return result, step
