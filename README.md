# PII Redaction Tool

This tool is a lightweight, high-performance PII (Personally Identifiable Information) Redaction Tool designed to process documents (Microsoft Word `.docx` and text files `.txt`) and redact sensitive information by replacing it with realistic, consistent fake alternatives.

## Approach & Design
Due to strict machine constraints (specifically, a full C: drive with only ~30 MB free space), heavy deep learning frameworks (such as Hugging Face transformers, PyTorch, or spaCy NER pipelines) could not be installed. 

Instead, this tool implements a **hybrid Rule-Based and Regex-driven engine with Contextual Heuristics** and a custom **Stemming Tokenizer** for named entity filtering:
1. **Regular Expressions**: Used for structured entities like Emails, IP addresses, Credit Cards, SSNs, and Dates of Birth.
2. **Luhn Algorithm Validation**: Ensures credit card numbers are verified mathematically before redaction, eliminating false positives from arbitrary 16-digit numbers (like product IDs).
3. **Contextual Label Matching**: Searches for surrounding label indicators (e.g., `Telephone:`, `Registered Office:`, `DOB:`, `residing at:`) to isolate phone numbers, addresses, and dates of birth.
4. **Negative Lookahead Boundaries**: Utilized in address extraction to prevent merging separate physical addresses that occur consecutively in the text.
5. **Stemming Tokenizer for Names & Companies**: Capitalized word sequences are parsed. Each word is checked against a massive blacklist of ~300 common English, legal, and corporate terms. We implement a custom stemmer (extracting word roots to filter out plurals/tenses, e.g., mapping `Working` to `work`, `Farms` to `farm`) to achieve high precision and recall.
6. **Consistent Entity Mapping**: Identifies unique real values and maps them consistently to unique fake counterparts throughout the entire document (e.g., replacing `Ajay Shriram Patil` with `Peter Parker` consistently, and his emails/phone numbers with corresponding fake entities).

## Tradeoffs and Observations
- **Tradeoff (Rule-Based vs. ML)**: Rule-based systems run instantly and do not require heavy models or GPU resources, which was critical for our server with 30MB free space. However, they require careful regex design to handle formatting differences (e.g. en-dash vs hyphens, spacing in Indian pin codes).
- **False Positives**: Capitalized labels (like `Working Days`, `Price Band`, or street-name elements like `Off Pallod Farms`) would initially be categorized as names. This was resolved by designing the lightweight stemming tokenizer that successfully filters out word roots of common terms.
- **False Negatives**: Addresses embedded without preceding labels (e.g. inside table cells) were originally missed. This was resolved by creating standalone structural address matchers targeting specific building/pincode patterns.

## How to Run the Tool

### Prerequisites
Install the required lightweight dependencies:
```bash
pip install python-docx
```

### Redacting a Document
To run the redactor on a docx or text file:
```bash
python redact_pii.py <input_file_path> <output_file_path>
```
*Example:*
```bash
python redact_pii.py "C:\Users\JANHAVI\Downloads\Red Herring Prospectus.docx" "Red_Herring_Prospectus_Redacted.docx"
```

### Running the Evaluation Suite
To run the automated evaluation suite and verify accuracy, precision, and recall metrics:
```bash
python evaluate.py
```
