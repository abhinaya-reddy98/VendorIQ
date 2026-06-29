"""Generate sample vendor PDF documents for testing VendorIQ."""
import fitz  # PyMuPDF
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "vendor_docs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_pdf(filename: str, content: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 80),
        content,
        fontsize=11,
        fontname="helv",
        color=(0, 0, 0),
    )
    path = os.path.join(OUTPUT_DIR, filename)
    doc.save(path)
    doc.close()
    print(f"Created: {path}")


# ─── GST Certificate ─────────────────────────────────────────────────────────
create_pdf(
    "gst_certificate.pdf",
    """GOODS AND SERVICES TAX REGISTRATION CERTIFICATE
Government of India – Ministry of Finance

This is to certify that the following taxpayer has been registered under the
Central Goods and Services Tax Act, 2017.

Company Name:   Nexus Manufacturing Pvt Ltd
GSTIN:          27AAECN1234F1Z5
Registration Type: Regular
Date of Registration: 12/03/2021
State:          Maharashtra
Address:        Plot No. 45, MIDC Industrial Area, Pune – 411019
Status:         Active

PAN of Business: AAECN1234F
Nature of Business: Manufacturing – Industrial Equipment

This certificate is valid unless cancelled or surrendered.

Issued by: GST Department, Government of India
Certificate Number: GST-MH-2021-789456
Date: 15/03/2021
""",
)

# ─── PAN Card ────────────────────────────────────────────────────────────────
create_pdf(
    "pan_card.pdf",
    """INCOME TAX DEPARTMENT – GOVERNMENT OF INDIA
PERMANENT ACCOUNT NUMBER CARD

Name of Assessee (Individual / Company):
NEXUS MANUFACTURING PVT LTD

Permanent Account Number:
AAECN1234F

Date of Issue: 05/01/2018
Status: Active
Type: Company

Father's Name / Director's Name: Rajesh Kumar Gupta

This PAN is issued under Section 139A of the Income Tax Act, 1961.
Any misuse of this document is a punishable offence.

Issued by: National Securities Depository Limited (NSDL)
on behalf of the Income Tax Department
""",
)

# ─── ISO Certificate ─────────────────────────────────────────────────────────
create_pdf(
    "iso_certificate.pdf",
    """CERTIFICATE OF CONFORMANCE
ISO 9001:2015 – Quality Management System

This is to certify that the Quality Management System of:

Organization Name: Nexus Manufacturing Pvt Ltd
Address: Plot No. 45, MIDC Industrial Area, Pune – 411019, Maharashtra

Has been assessed and found to conform to the requirements of:
ISO 9001:2015

Scope of Certification:
Design, Manufacture, and Supply of Industrial Equipment and Components

Certificate Number: ISO-QMS-2021-MH-45678
Accreditation Body: Quality Council of India (QCI)
Certification Body: Bureau Veritas Certification India Pvt Ltd

Date of Initial Certification: 10/04/2021
Valid From: 10/04/2024
Valid Until (Expiry Date): 09/04/2027
Date of Issue: 10/04/2024

Signed by: Michael Thompson
Head of Certification, Bureau Veritas

This certificate is subject to annual surveillance audits.
""",
)

# ─── Factory Audit Report ─────────────────────────────────────────────────────
create_pdf(
    "factory_audit_report.pdf",
    """FACTORY AUDIT REPORT
VendorIQ Procurement Compliance Audit

Audit Reference: AUDIT-2024-PUN-09876
Vendor: Nexus Manufacturing Pvt Ltd
Audit Date: 15/01/2024
Auditors: Priya Sharma, Senior Auditor; Vikram Nair, Technical Expert

AUDIT SCORES BY CATEGORY:
──────────────────────────────────────────
Quality Management System:       22/25
Manufacturing Processes:         21/25
Safety & Environmental:          20/25
Documentation & Compliance:      23/25
──────────────────────────────────────────
TOTAL Audit Score:               86/100
──────────────────────────────────────────

FINDINGS:
✓ Quality management system well-established and documented
✓ Clean manufacturing environment with modern equipment
✓ Workers trained on safety protocols
✓ All ISO procedures followed
△ Minor: Storage area needs better labelling (corrective action in progress)
△ Minor: 2 calibration records overdue for renewal

OVERALL ASSESSMENT: SATISFACTORY
Vendor meets all minimum quality thresholds for supplier approval.

Recommended: APPROVE for Tier-1 Supplier Status

Next Audit Due: January 2025
Audit Validity: 12 months from date of issue
""",
)

# ─── Bank Details ─────────────────────────────────────────────────────────────
create_pdf(
    "bank_details.pdf",
    """VENDOR BANK DETAILS DECLARATION

I/We hereby declare that the following bank account details are correct
and belong to our company for the purpose of vendor payments.

Company Name: Nexus Manufacturing Pvt Ltd
Company PAN: AAECN1234F
GST Number: 27AAECN1234F1Z5

Bank Details:
─────────────────────────────────────────────
Bank Name:        HDFC Bank Ltd
Branch:           Pune – Pimpri Branch
Account Number:   50100123456789
Account Type:     Current Account
IFSC Code:        HDFC0001234
MICR Code:        411240001
─────────────────────────────────────────────

Account Holder Name (as per bank records): Nexus Manufacturing Pvt Ltd

Enclosed: Cancelled Cheque / Bank Statement

Declaration:
We confirm that the above bank account is in the company's name and
will be used for all vendor payments from the enterprise.

Authorized Signatory: Rajesh Kumar Gupta
Designation: Managing Director
Date: 10/01/2024
Company Seal: [SEAL]
""",
)

# ─── Company Registration Certificate ────────────────────────────────────────
create_pdf(
    "registration_certificate.pdf",
    """MINISTRY OF CORPORATE AFFAIRS
REGISTRAR OF COMPANIES – MAHARASHTRA, PUNE

CERTIFICATE OF INCORPORATION

This is to certify that:

NEXUS MANUFACTURING PRIVATE LIMITED

is hereby incorporated under the Companies Act, 2013,
as a Private Limited Company.

Corporate Identification Number (CIN): U28910MH2015PTC267543
Date of Incorporation: 22/09/2015
Registration Number: 267543

Registered Office Address:
Plot No. 45, MIDC Industrial Area,
Pimpri-Chinchwad, Pune – 411019, Maharashtra, India

Nature of Business: Manufacturing – Industrial Equipment & Components
Authorized Capital: INR 1,00,00,000 (One Crore Rupees)
Paid-up Capital: INR 75,00,000 (Seventy-Five Lakh Rupees)

This certificate is issued under the seal of the Registrar of Companies.

Registrar of Companies
Maharashtra, Pune
Date: 25/09/2015
Reference: ROC/MH/Pune/2015/267543
""",
)

# ─── Security Questionnaire ───────────────────────────────────────────────────
create_pdf(
    "security_questionnaire.pdf",
    """VENDOR SECURITY & COMPLIANCE QUESTIONNAIRE
VendorIQ – Information Security Assessment

Vendor: Nexus Manufacturing Pvt Ltd
Contact: security@nexusmfg.com
Date Completed: 05/02/2024

SECTION 1: DATA SECURITY
Q1. Do you have an Information Security Policy? YES
Q2. ISO 27001 certified? NO (SOC 2 Type I in progress)
Q3. Data encrypted in transit and at rest? YES (AES-256)
Q4. Access control policy implemented? YES
Q5. Background checks on employees with data access? YES

SECTION 2: NETWORK SECURITY
Q6. Firewall and intrusion detection systems deployed? YES
Q7. Regular penetration testing conducted? YES (annually)
Q8. Secure VPN for remote access? YES
Q9. Network segmentation for sensitive systems? YES

SECTION 3: INCIDENT MANAGEMENT
Q10. Documented incident response plan? YES
Q11. Data breach notification policy within 72 hrs? YES
Q12. Security awareness training for staff? YES (quarterly)

SECTION 4: VENDOR MANAGEMENT
Q13. Third-party security assessments? YES (annually)
Q14. GDPR/data protection compliance? YES

SECURITY SCORE: 78/100
Assessment Result: MODERATE RISK – Proceed with standard controls
Note: Recommend ISO 27001 certification within 12 months.

Reviewed by: Security Team, VendorIQ
Review Date: 10/02/2024
""",
)

# ─── Email Conversation ───────────────────────────────────────────────────────
create_pdf(
    "email_conversation.pdf",
    """EMAIL THREAD – VENDOR ONBOARDING CORRESPONDENCE

──────────────────────────────────────────────────────────────
From: procurement@enterprise.com
To: rajesh.gupta@nexusmfg.com
Date: 08/01/2024
Subject: Vendor Onboarding – Document Submission Request
──────────────────────────────────────────────────────────────
Dear Mr. Gupta,

Thank you for expressing interest in becoming an approved vendor.

Please submit the following documents for our evaluation:
1. GST Registration Certificate
2. PAN Card (Company)
3. ISO 9001 Certificate
4. Factory Audit Report (within 12 months)
5. Bank Account Details with Cancelled Cheque
6. Company Registration Certificate
7. Security Questionnaire (attached)

Regards,
Sarah Mitchell
Senior Procurement Manager

──────────────────────────────────────────────────────────────
From: rajesh.gupta@nexusmfg.com
To: procurement@enterprise.com
Date: 10/01/2024
Subject: RE: Vendor Onboarding – Document Submission
──────────────────────────────────────────────────────────────
Dear Ms. Mitchell,

Thank you for the onboarding request. We are pleased to submit
all required documents as requested.

Company Overview:
- Nexus Manufacturing Pvt Ltd, established 2015
- 12 years combined experience in industrial equipment manufacturing
- Current clients include Tata Motors, L&T, Bosch India
- Annual turnover: INR 45 Crores (FY 2022-23)
- Total employees: 280 (60% skilled manufacturing staff)

Please find all documents attached. We look forward to a
successful business relationship.

Best regards,
Rajesh Kumar Gupta
Managing Director – Nexus Manufacturing Pvt Ltd
Email: rajesh.gupta@nexusmfg.com
Phone: +91-98765-43210
""",
)

print("\n✅ All sample vendor documents created successfully!")
print(f"📁 Location: {OUTPUT_DIR}")
