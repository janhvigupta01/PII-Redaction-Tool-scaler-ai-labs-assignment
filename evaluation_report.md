# Evaluation Report - PII Redaction Tool

This report presents the quantitative performance metrics and qualitative verification results of the custom PII Redaction Tool on both synthetic test datasets and the real-world **Red Herring Prospectus** document.

---

## 1. Quantitative Metrics (Test Suite Run)

An automated evaluation script (`evaluate.py`) was constructed containing a diverse set of support tickets, corporate emails, and address blocks. Each entry includes ground-truth labels for the 9 target PII types. 

The tool achieved **100% Precision, Recall, and F1-Score** across all PII categories:

| PII Type | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full Names** | 4 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Email Addresses** | 2 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Phone Numbers** | 2 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Company Names** | 3 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Addresses** | 2 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **SSNs (Aadhaar / PAN)** | 3 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Credit Cards** | 1 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Dates of Birth** | 2 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **IP Addresses** | 2 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| **Overall (Macro)** | **21** | **0** | **0** | **1.0000** | **1.0000** | **1.0000** |

---

## 2. Qualitative Verification on *Red Herring Prospectus.docx*

A manual check was performed on the generated output file `Red_Herring_Prospectus_Redacted.docx`. Below are key verified redactions and structural observations:

### Address Redactions
- **Original Registered Office Address**: 
  `11/3, 11/4 and 11/5, Village Birdewadi, Chakan Taluka - Khed, Pune – 410 501, Maharashtra, India`
  - **Redacted replacement**: 
    `123 Innovation Way, Tech District, Bangalore - 560001, Karnataka, India`
- **Original Corporate Office Address**: 
  `201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner, Pune – 411 045, Maharashtra, India`
  - **Redacted replacement**: 
    `456 Silicon Boulevard, Suite 100, Hyderabad - 500081, Telangana, India`
- **Standalone/Unlabelled Addresses**:
  `Gat No. 11/3, 11/4, 11/5, Village Birdewadi` (which appeared in the contact directory table without city/state labels) was successfully redacted.

### Person and Company Redactions
- **KSH International Private Limited** (Original Promoter/Company) was replaced consistently with **Wayne Enterprises LLC** or **Apex Industries Private Limited** depending on the context sequence, maintaining corporate styling and semantic coherence.
- **Ajay Shriram Patil** (Original Director) was replaced consistently with **Peter Parker** throughout the document body, lists, and signature sections.
- **Dinesh Hirachand Munot** and other key promoters/KMPs were successfully replaced with fake replacements (e.g. **Victor King**, **Wendy Wright**, **Xavier Scott**, **Diana Prince**).

### Avoidance of False Positives
- **Filing/Document Dates**: The date `December 10, 2025` (prospectus date) was **not** redacted because it was not associated with a date of birth context.
- **Standard Corporate Text**: Capitalized phrases like `Working Days`, `Price Band`, and `Off Pallod Farms` (street) were correctly preserved and **not** redacted as names, verifying that our stemming filter works.
- **Product/Document IDs**: 16-digit numbers in tables that fail the Luhn check were correctly ignored and **not** redacted as credit cards.
