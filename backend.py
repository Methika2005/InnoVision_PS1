"""
backend.py — Synapse Green-Truth Auditor
========================================
Single source of truth for ALL logic.
- Notebook (Synapse_3.ipynb) imports from here to run experiments / evaluation.
- app.py imports from here to display results.
Neither file contains any scoring / classification logic of its own.
"""

import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

BUZZWORDS = [
    "eco-friendly", "green", "natural", "sustainable", "conscious",
    "ethical", "clean", "planet-friendly", "earth-conscious", "non-toxic",
    "biodegradable", "organic", "eco-conscious", "responsible", "pure",
    "carbon neutral", "net zero", "zero waste", "environmentally friendly",
    "loved by nature", "free from harmful chemicals", "toxin-free",
    "chemical-free", "nature-inspired", "plant-based", "earth-friendly",
    "safe for the planet", "free from", "no harmful", "gentle on earth",
    "cruelty-free", "vegan", "clean beauty", "green beauty",
    "sustainability", "climate", "fossil-free", "pre-loved",
    "circular", "commitments", "ambition", "targets", "decarbonise",
]

FUTURE_PROMISES = [
    "aim to", "committed to", "by 2030", "by 2040", "by 2050", "goal is",
    "working towards", "our ambition", "roadmap", "in the future", "strive to",
    "mission to", "pledge",
]

EVIDENCE_KEYWORDS = [
    'according to', 'verified by', 'audited by', 'reported by',
    'certified', 'certification', 'gots', 'b-corp', 'oeko-tex',
    'third party', 'third-party', 'accredited', 'iso', 'standard',
    'control union', 'bureau veritas', 'rainforest alliance',
    'bis ecomark', 'ecomark', 'greenpro', 'cii greenpro',
    'asci', 'isi mark', 'score of', 'independently verified',
]

EVIDENCE_PATTERNS = [
    r'\d+%', r'certified', r'certification', r'gots', r'b-corp', r'oeko-tex',
    r'audited', r'audit', r'third[\s\-]?party', r'verified', r'accredited',
    r'iso\s*\d+', r'control union', r'bureau veritas', r'bis ecomark',
    r'ecomark', r'greenpro', r'rainforest alliance', r'score of \d+',
]

CERT_NAMES = [
    'gots', 'b-corp', 'oeko-tex', 'rainforest alliance', 'fair trade',
    'control union', 'bureau veritas', 'bis ecomark', 'ecomark', 'greenpro',
    'cii greenpro', 'asci', 'isi mark',
]

ENVIRONMENTAL_TOPICS = BUZZWORDS + FUTURE_PROMISES + EVIDENCE_KEYWORDS + [
    "material", "fabric", "cotton", "wool", "polyester", "plastic", "leather",
    "carbon", "emissions", "water", "energy", "waste", "footprint", "impact",
    "supply chain", "factory", "workers", "packaging", "recycled", "recycling",
    "climate", "environment", "ingredients", "sourcing", "agriculture",
    "forestry", "biodiversity", "renewable", "solar", "power", "manufacturing",
]

LABELS = [
    "vague marketing or future promises",
    "specific and verifiable environmental evidence",
]


# ─────────────────────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────────────────────

def load_model():
    """Load and return the zero-shot NLI classifier."""
    return pipeline(
        "zero-shot-classification",
        model="cross-encoder/nli-MiniLM2-L6-H768",
    )


def load_databases(
    bcorp_path="bcorp.csv",
    gots_path="gots.csv",
    india_path="indian_certifications.csv",
):
    """
    Load certification databases from CSV files.
    Returns (bcorp_df, gots_df, india_df).
    Raises FileNotFoundError with a clear message if a file is missing.
    """
    bcorp = pd.read_csv(bcorp_path)
    gots  = pd.read_csv(gots_path)
    india = pd.read_csv(india_path)

    if "certification_type" in bcorp.columns:
        bcorp = bcorp.rename(columns={"certification_type": "cert_type"})

    for df in (bcorp, gots, india):
        df["cert_type"] = df["cert_type"].fillna("None")

    return bcorp, gots, india


# ─────────────────────────────────────────────────────────────
# HELPERS — pure functions, no side effects
# ─────────────────────────────────────────────────────────────

def is_relevant(sentence: str) -> bool:
    """Return True if the sentence discusses environment / product claims."""
    lo = sentence.lower()
    return any(t in lo for t in ENVIRONMENTAL_TOPICS)


def has_buzzword(sentence: str):
    """Return (bool, list_of_matched_buzzwords)."""
    lo = sentence.lower()
    found = [w for w in BUZZWORDS if w in lo]
    return bool(found), found


def has_future_promise(sentence: str):
    """Return (bool, list_of_matched_promise_phrases)."""
    lo = sentence.lower()
    found = [w for w in FUTURE_PROMISES if w in lo]
    return bool(found), found


def has_evidence(sentence: str) -> bool:
    """Return True if any evidence pattern is found."""
    lo = sentence.lower()
    return any(re.search(p, lo) for p in EVIDENCE_PATTERNS)


def has_unverified_stat(sentence: str) -> bool:
    """Return True if a big number appears without a cited source."""
    lo = sentence.lower()
    big_number = bool(re.search(r'\d+\s*(million|billion|ton|tons|kg|lbs)', lo))
    has_source = any(w in lo for w in EVIDENCE_KEYWORDS)
    return big_number and not has_source


def check_brands(text: str, bcorp, gots, india) -> list:
    """
    Return list of brand match dicts found in text across all three databases.
    Each dict: {brand, certified, cert_type, database}
    """
    lo = text.lower()
    matches = []
    for db, db_name in [(bcorp, "B-Corp"), (gots, "GOTS"), (india, "India")]:
        for _, row in db.iterrows():
            bl = str(row["brand"]).lower()
            if re.search(r'\b' + re.escape(bl) + r'\b', lo):
                matches.append({
                    "brand":     row["brand"],
                    "certified": bool(row["certified"]),
                    "cert_type": str(row["cert_type"]),
                    "database":  db_name,
                })
    return matches


def verify_cert_claim(sentence: str, brand_matches: list):
    """
    If sentence mentions a tracked certification, check it against brand_matches.
    Returns (is_verified: bool, cert_name_or_None).
    """
    lo = sentence.lower()
    for cert in CERT_NAMES:
        if cert in lo:
            ok = any(
                cert.lower() in str(r["cert_type"]).lower() and r["certified"]
                for r in brand_matches
            )
            if not ok:
                return False, cert.upper()
    return True, None


# ─────────────────────────────────────────────────────────────
# CORE: sentence classification
# ─────────────────────────────────────────────────────────────

def classify_sentence(sentence: str, classifier, brand_matches: list) -> dict:
    """
    Classify a single sentence and return a result dict:
    {verdict, score, flagged, reason}
    Decision tree order:
      1. Future promise (no evidence) → Future Promise
      2. Has evidence → check for unverified stat or fake cert, else Backed
      3. No evidence + unverified stat → Unverified Statistic
      4. No evidence + buzzword → Vague
      5. Fallback → NLI classifier → Evidence-Based or Uncertain/PR Speak
    """
    bw_found, bw_list = has_buzzword(sentence)
    fp_found, fp_list = has_future_promise(sentence)
    ev = has_evidence(sentence)

    # Rule 1 — Future promise with no backing evidence
    if fp_found and not ev:
        return {
            "verdict": "Future Promise (Not Evidence)",
            "score":   0.3,
            "flagged": fp_list,
            "reason":  "Corporate goals and future pledges are not current verifiable facts.",
        }

    # Rule 2 — Evidence present
    if ev:
        if has_unverified_stat(sentence):
            return {
                "verdict": "Unverified Statistic",
                "score":   0.2,
                "flagged": bw_list,
                "reason":  "Numbers used without an auditor or certification source.",
            }
        ok, cert = verify_cert_claim(sentence, brand_matches)
        if not ok:
            return {
                "verdict": "Fake Certification Claim",
                "score":   0.0,
                "flagged": bw_list,
                "reason":  f"Brand not found in our {cert} database as certified.",
            }
        return {
            "verdict": "Backed Claim",
            "score":   0.9,
            "flagged": bw_list,
            "reason":  "References a valid certification or verified evidence.",
        }

    # Rule 3 — Unverified statistic (no evidence keywords)
    if has_unverified_stat(sentence):
        return {
            "verdict": "Unverified Statistic",
            "score":   0.2,
            "flagged": [],
            "reason":  "Numbers used without any source, auditor, or certification.",
        }

    # Rule 4 — Pure buzzwords, no evidence
    if bw_found:
        return {
            "verdict": "Vague",
            "score":   0.0,
            "flagged": bw_list,
            "reason":  "Uses sustainability buzzwords with no evidence or certification.",
        }

    # Rule 5 — NLI classifier fallback
    result = classifier(sentence, LABELS)
    label  = result["labels"][0]
    conf   = result["scores"][0]

    if label == LABELS[1] and conf > 0.6:
        return {
            "verdict": "Evidence-Based",
            "score":   round(conf, 2),
            "flagged": [],
            "reason":  "AI found specific environmental evidence despite no buzzwords.",
        }
    return {
        "verdict": "Uncertain / PR Speak",
        "score":   0.4,
        "flagged": [],
        "reason":  "AI classified this as vague marketing or general corporate PR.",
    }


# ─────────────────────────────────────────────────────────────
# CORE: full audit
# ─────────────────────────────────────────────────────────────

def audit_text(text: str, classifier, bcorp, gots, india) -> dict:
    """
    Run the full greenwash audit on a block of text.

    Returns:
    {
        sentences:     list of per-sentence result dicts (with 'sentence' key),
        final_score:   float 0–1,
        overall:       str  "Greenwashing Likely" | "Uncertain" | "Legitimate Claims",
        brand_matches: list of brand match dicts,
        total_valid:   int  (sentences that were environmental claims),
    }
    """
    raw_sentences = [
        s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10
    ]
    brand_matches = check_brands(text, bcorp, gots, india)

    all_results  = []
    valid_claims = []

    for s in raw_sentences:
        if not is_relevant(s):
            all_results.append({
                "verdict":  "Ignored (Website Noise)",
                "score":    0.0,
                "flagged":  [],
                "reason":   "Standard website text — no environmental claim detected.",
                "sentence": s,
            })
            continue

        r = classify_sentence(s, classifier, brand_matches)
        r["sentence"] = s
        all_results.append(r)
        valid_claims.append(r)

    # Score = mean of valid claim scores
    final_score = (
        round(sum(r["score"] for r in valid_claims) / len(valid_claims), 2)
        if valid_claims else 0.0
    )

    # Penalty: known uncertified brand mentioned
    if any(m["certified"] is False for m in brand_matches):
        final_score = round(max(0.0, final_score - 0.40), 2)

    # Overall verdict
    if final_score < 0.4:
        overall = "Greenwashing Likely"
    elif final_score < 0.7:
        overall = "Uncertain"
    else:
        overall = "Legitimate Claims"

    return {
        "sentences":     all_results,
        "final_score":   final_score,
        "overall":       overall,
        "brand_matches": brand_matches,
        "total_valid":   len(valid_claims),
    }


# ─────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────

def scrape_url(url: str) -> str | None:
    """
    Fetch a URL and return clean text (up to 3000 chars), or None on failure.
    """
    try:
        res = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=". ", strip=True)[:3000]
    except Exception:
        return None


def verdict_from_report(report: dict) -> int:
    """
    Convert a full audit report to a binary label.
    1 = Legitimate, 0 = Greenwashing / Uncertain.
    Used by the notebook for model evaluation.
    """
    return 1 if report["overall"] == "Legitimate Claims" else 0
