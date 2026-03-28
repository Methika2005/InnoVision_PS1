# ════════════════════════════════════════════════════════════
# CELL 0 — Replace your existing imports / logic with this
# All logic now lives in backend.py. Notebook just uses it.
# ════════════════════════════════════════════════════════════

from backend import (
    load_model,
    load_databases,
    audit_text,
    scrape_url,
    verdict_from_report,
    # constants (if you need them for EDA / debugging)
    BUZZWORDS,
    FUTURE_PROMISES,
    EVIDENCE_KEYWORDS,
    LABELS,
)

# Load resources
classifier         = load_model()
bcorp, gots, india = load_databases()

print("✅ Backend loaded. classifier, bcorp, gots, india are ready.")


# ════════════════════════════════════════════════════════════
# CELL — Run an audit (replaces your old audit_product calls)
# ════════════════════════════════════════════════════════════

sample_text = """
Our jacket is made from 100% recycled ocean plastics.
We are committed to becoming carbon neutral by 2030.
Certified by GOTS for sustainable cotton sourcing.
H&M uses eco-friendly materials across all product lines.
"""

report = audit_text(sample_text, classifier, bcorp, gots, india)

print(f"Score  : {report['final_score']}")
print(f"Verdict: {report['overall']}")
print(f"Claims : {report['total_valid']} environmental sentences analysed")
print()
for r in report["sentences"]:
    print(f"  [{r['verdict']:35s}] {r['sentence'][:80]}")


# ════════════════════════════════════════════════════════════
# CELL — Evaluation (same as before, now uses backend)
# ════════════════════════════════════════════════════════════

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

test_df = pd.read_csv("test_data.csv")

# verdict_from_report converts full report → binary label
test_df["predicted"] = test_df["text"].apply(
    lambda t: verdict_from_report(audit_text(t, classifier, bcorp, gots, india))
)

print("Accuracy:", accuracy_score(test_df["label"], test_df["predicted"]))
print(classification_report(test_df["label"], test_df["predicted"]))
