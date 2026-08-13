#!/usr/bin/env python3
import os
import re
from redact_pii import PIIRedactor

# Evaluation Test Suite (Ground Truth Labels)
# format: text, list of {"start", "end", "type", "val"}
test_cases = [
    {
        "text": "Ticket #1024: User Rashi Patil reported login issues from IP 192.168.1.105.",
        "pii": [
            {"start": 19, "end": 30, "type": "name", "val": "Rashi Patil"},
            {"start": 61, "end": 74, "type": "ip", "val": "192.168.1.105"}
        ]
    },
    {
        "text": "Email: rashhi.patil@gmail.com, Mobile: +91 9876543210, Country: India.",
        "pii": [
            {"start": 7, "end": 29, "type": "email", "val": "rashhi.patil@gmail.com"},
            {"start": 39, "end": 53, "type": "phone", "val": "+91 9876543210"}
        ]
    },
    {
        "text": "Please ship the items to Rohan Dey, residing at 201, Tower 2, Montreal Business Centre, Pune - 411045, India.",
        "pii": [
            {"start": 25, "end": 34, "type": "name", "val": "Rohan Dey"},
            {"start": 48, "end": 109, "type": "address", "val": "201, Tower 2, Montreal Business Centre, Pune - 411045, India"}
        ]
    },
    {
        "text": "The contract was signed by Rajesh Dinesh Munot of KSH International Private Limited.",
        "pii": [
            {"start": 27, "end": 46, "type": "name", "val": "Rajesh Dinesh Munot"},
            {"start": 50, "end": 83, "type": "company", "val": "KSH International Private Limited"}
        ]
    },
    {
        "text": "His date of birth is 15-08-1990 and his US SSN is 321-45-9876.",
        "pii": [
            {"start": 21, "end": 31, "type": "dob", "val": "15-08-1990"},
            {"start": 50, "end": 61, "type": "ssn", "val": "321-45-9876"}
        ]
    },
    {
        "text": "Payment made using Visa card 4111-1111-1111-1111. Please verify.",
        "pii": [
            {"start": 29, "end": 48, "type": "cc", "val": "4111-1111-1111-1111"}
        ]
    },
    {
        "text": "Company: Nuvama Wealth Management Ltd. registered office at 11/3, Chakan Taluka, Pune – 410501.",
        "pii": [
            {"start": 9, "end": 38, "type": "company", "val": "Nuvama Wealth Management Ltd."},
            {"start": 60, "end": 94, "type": "address", "val": "11/3, Chakan Taluka, Pune – 410501"}
        ]
    },
    {
        "text": "Audit report by ICICI Securities Ltd. on 2025-12-10 (not a DOB).",
        "pii": [
            {"start": 16, "end": 36, "type": "company", "val": "ICICI Securities Ltd."}
            # Note: "2025-12-10" is NOT a date of birth and should NOT be redacted.
        ]
    },
    {
        "text": "Contact person: Mr. Ajay Shriram Patil, phone: 8879770456, email: ksh.ipo@nuvama.com.",
        "pii": [
            {"start": 20, "end": 38, "type": "name", "val": "Ajay Shriram Patil"},
            {"start": 47, "end": 57, "type": "phone", "val": "8879770456"},
            {"start": 66, "end": 84, "type": "email", "val": "ksh.ipo@nuvama.com"}
        ]
    },
    {
        "text": "My Aadhaar Number is 1234 5678 9012 and my PAN card is ABCDE1234F.",
        "pii": [
            {"start": 21, "end": 35, "type": "ssn", "val": "1234 5678 9012"},
            {"start": 55, "end": 65, "type": "ssn", "val": "ABCDE1234F"}
        ]
    },
    {
        "text": "Customer database server IP is 10.0.0.1. Port 8080 is open.",
        "pii": [
            {"start": 31, "end": 39, "type": "ip", "val": "10.0.0.1"}
        ]
    },
    {
        "text": "Born on October 24, 1985 in a small village near Chakan.",
        "pii": [
            {"start": 8, "end": 24, "type": "dob", "val": "October 24, 1985"}
        ]
    },
    {
        "text": "Please check card number 1234-5678-1234-5678 (invalid Luhn).",
        "pii": [
            # Invalid Luhn, should NOT be redacted as a credit card (precision check)
        ]
    }
]

def calculate_metrics():
    redactor = PIIRedactor()
    
    # Track statistics per PII type
    # Keys: name, email, phone, company, address, ssn, cc, dob, ip
    stats = {}
    pii_types = ["name", "email", "phone", "company", "address", "ssn", "cc", "dob", "ip"]
    for t in pii_types:
        stats[t] = {"tp": 0, "fp": 0, "fn": 0}
        
    print("=== STARTING PII REDACTION EVALUATION ===")
    
    for i, case in enumerate(test_cases):
        text = case["text"]
        ground_truth = case["pii"]
        
        # Run redactor
        redacted_text, predictions = redactor.redact_text(text)
        
        # Check predictions against ground truth
        # Keep track of which ground truth and predictions are matched
        matched_gt = set()
        matched_pred = set()
        
        # Match predicted spans to ground truth spans
        for pred_idx, pred in enumerate(predictions):
            p_start, p_end, p_type = pred["start"], pred["end"], pred["type"]
            p_val = pred["orig"]
            
            # Find an overlapping ground truth with the same type
            found_match = False
            for gt_idx, gt in enumerate(ground_truth):
                g_start, g_end, g_type = gt["start"], gt["end"], gt["type"]
                
                # Check for overlap and type match
                # Overlap check: max(p_start, g_start) < min(p_end, g_end)
                if p_type == g_type and max(p_start, g_start) < min(p_end, g_end):
                    stats[p_type]["tp"] += 1
                    matched_gt.add(gt_idx)
                    matched_pred.add(pred_idx)
                    found_match = True
                    break
                    
            if not found_match:
                stats[p_type]["fp"] += 1
                
        # Any unmatched ground truth is a False Negative
        for gt_idx, gt in enumerate(ground_truth):
            if gt_idx not in matched_gt:
                stats[gt["type"]]["fn"] += 1
                print(f"  [MISS/FN] Test case {i+1}: Missed ground truth '{gt['val']}' ({gt['type']})")
                
    # Calculate Precision, Recall, and F1 for each class
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    report_lines = []
    report_lines.append("| PII Type | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Precision | Recall | F1-Score |")
    report_lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    
    print("\n=== EVALUATION REPORT ===")
    print(f"{'PII Type':<15} | {'TP':<5} | {'FP':<5} | {'FN':<5} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9}")
    print("-" * 75)
    
    for t in pii_types:
        tp = stats[t]["tp"]
        fp = stats[t]["fp"]
        fn = stats[t]["fn"]
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0
        
        print(f"{t:<15} | {tp:<5} | {fp:<5} | {fn:<5} | {precision:.4f}    | {recall:.4f}    | {f1:.4f}")
        report_lines.append(f"| {t} | {tp} | {fp} | {fn} | {precision:.4f} | {recall:.4f} | {f1:.4f} |")
        
    print("-" * 75)
    macro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    macro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall) if (macro_precision + macro_recall) > 0 else 1.0
    print(f"{'Overall (Macro)':<15} | {total_tp:<5} | {total_fp:<5} | {total_fn:<5} | {macro_precision:.4f}    | {macro_recall:.4f}    | {macro_f1:.4f}")
    
    report_lines.append(f"| **Overall** | **{total_tp}** | **{total_fp}** | **{total_fn}** | **{macro_precision:.4f}** | **{macro_recall:.4f}** | **{macro_f1:.4f}** |")
    
    # Save evaluation report to markdown file in the workspace
    with open('evaluation_report_metrics.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

if __name__ == "__main__":
    calculate_metrics()
