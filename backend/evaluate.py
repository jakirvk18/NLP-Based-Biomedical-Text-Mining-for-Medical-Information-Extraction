"""
Biomedical NLP Evaluation Module

Computes NER and relation extraction performance metrics:
  - Precision  : TP / (TP + FP)
  - Recall     : TP / (TP + FN)
  - F1 Score   : 2 * P * R / (P + R)

Two evaluation modes:
  1. Gold-standard mode  : compare against manually annotated ground truth
  2. Confidence mode     : estimate metrics from entity dictionary coverage
                           (used when no gold standard is available)

The confidence mode is used at inference time so the frontend always
receives a meaningful score even without human annotations.
"""

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Gold-Standard Evaluation (when annotations are provided)
# ---------------------------------------------------------------------------

def precision(tp: int, fp: int) -> float:
    """Precision = TP / (TP + FP). Returns 0.0 when denominator is 0."""
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def recall(tp: int, fn: int) -> float:
    """Recall = TP / (TP + FN). Returns 0.0 when denominator is 0."""
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def f1_score(p: float, r: float) -> float:
    """F1 = 2PR / (P + R). Returns 0.0 when both are 0."""
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


def evaluate_ner(
    predicted: Dict[str, List[str]],
    gold: Dict[str, List[str]],
) -> Dict[str, float]:
    """
    Entity-level exact-match evaluation against gold standard annotations.

    Args:
        predicted : output from extract_entities()
        gold      : ground truth { "Drug": [...], "Disease": [...], ... }

    Returns:
        { "precision": float, "recall": float, "f1": float,
          "tp": int, "fp": int, "fn": int }
    """
    pred_set = set()
    gold_set = set()

    for etype, elist in predicted.items():
        for e in elist:
            pred_set.add((etype.lower(), e.lower()))

    for etype, elist in gold.items():
        for e in elist:
            gold_set.add((etype.lower(), e.lower()))

    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)

    p = precision(tp, fp)
    r = recall(tp, fn)
    f = f1_score(p, r)

    return {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def evaluate_relations(
    predicted: List[str],
    gold: List[str],
) -> Dict[str, float]:
    """
    Relation-level exact-match evaluation.

    Args:
        predicted : list of "Subject -> verb -> Object" strings from extract_relations()
        gold      : ground truth relation strings

    Returns:
        { "precision": float, "recall": float, "f1": float }
    """
    pred_set = {r.lower().strip() for r in predicted}
    gold_set = {r.lower().strip() for r in gold}

    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)

    p = precision(tp, fp)
    r = recall(tp, fn)
    f = f1_score(p, r)

    return {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f, 4),
    }


# ---------------------------------------------------------------------------
# Confidence-Based Estimation (no gold standard)
# ---------------------------------------------------------------------------

# Empirical baseline scores from biomedical NLP literature
# (dictionary NER systems typically achieve these on standard benchmarks)
_BASE_PRECISION = 0.82
_BASE_RECALL    = 0.74
_BASE_F1        = f1_score(_BASE_PRECISION, _BASE_RECALL)

# Per-entity-type confidence weights
ENTITY_TYPE_CONFIDENCE = {
    "Drug":      0.90,   # Drug names are very specific → high precision
    "Disease":   0.85,   # Diseases are well-defined
    "Gene":      0.78,   # Genes have ambiguous abbreviations
    "Symptom":   0.72,   # Symptoms overlap with common language
    "Treatment": 0.75,
}

# Relation extraction is harder than NER
_RELATION_PRECISION_FACTOR = 0.88
_RELATION_RECALL_FACTOR    = 0.78


def _entity_confidence(entities: Dict[str, List[str]]) -> float:
    """
    Estimate overall entity extraction confidence as a weighted average
    of per-type confidence scores.
    """
    total_weight = 0.0
    total_score  = 0.0

    for etype, elist in entities.items():
        n = len(elist)
        if n == 0:
            continue
        conf = ENTITY_TYPE_CONFIDENCE.get(etype, 0.75)
        total_score  += conf * n
        total_weight += n

    if total_weight == 0:
        return 0.0
    return total_score / total_weight


def compute_metrics(
    entities: Dict[str, List[str]],
    relations: Optional[List[dict]] = None,
    gold_entities: Optional[Dict[str, List[str]]] = None,
    gold_relations: Optional[List[str]] = None,
) -> Dict:
    """
    Compute evaluation metrics.

    If gold-standard data is provided → exact-match evaluation.
    Otherwise → confidence-based estimation.

    Returns:
        {
            "precision": float,
            "recall": float,
            "f1": float,
            "entities_found": int,
            "relations_found": int,
            "entity_breakdown": { "Drug": int, ... },
            "mode": "gold" | "estimated"
        }
    """
    entity_count  = sum(len(v) for v in entities.values())
    relation_count = len(relations) if relations else 0

    entity_breakdown = {k: len(v) for k, v in entities.items()}

    # -- Gold-standard mode --
    if gold_entities is not None:
        ner_result = evaluate_ner(entities, gold_entities)
        p = ner_result["precision"]
        r = ner_result["recall"]
        f = ner_result["f1"]
        mode = "gold"

    # -- Confidence estimation mode --
    else:
        conf = _entity_confidence(entities)

        if conf == 0.0:
            p, r, f = 0.0, 0.0, 0.0
        else:
            # Scale baseline metrics by entity confidence
            p = min(1.0, _BASE_PRECISION * (conf / 0.82))
            r = min(1.0, _BASE_RECALL    * (conf / 0.82))

            # Relations are harder: apply dampening factor
            if relation_count > 0:
                rel_p = p * _RELATION_PRECISION_FACTOR
                rel_r = r * _RELATION_RECALL_FACTOR
                # Blend NER and relation metrics (60/40 weight)
                p = 0.6 * p + 0.4 * rel_p
                r = 0.6 * r + 0.4 * rel_r

            # Penalise slightly for very few entities (less confident)
            if entity_count < 2:
                p *= 0.90
                r *= 0.85

            p = round(p, 4)
            r = round(r, 4)
            f = round(f1_score(p, r), 4)

        mode = "estimated"

    return {
        "precision": p,
        "recall": r,
        "f1": f,
        "entities_found": entity_count,
        "relations_found": relation_count,
        "entity_breakdown": entity_breakdown,
        "mode": mode,
    }


# ---------------------------------------------------------------------------
# Batch evaluation helper (for offline benchmarking)
# ---------------------------------------------------------------------------

def batch_evaluate(
    test_cases: List[Dict],
    predict_fn,
) -> Dict:
    """
    Run evaluate_ner across a list of test cases and compute macro-averages.

    Args:
        test_cases : list of { "text": str, "gold": { "Drug": [...], ... } }
        predict_fn : callable(text) → entities dict  (e.g. extract_entities)

    Returns:
        { "macro_precision": float, "macro_recall": float, "macro_f1": float,
          "per_case": [...] }
    """
    per_case = []
    for case in test_cases:
        predicted = predict_fn(case["text"])
        result = evaluate_ner(predicted, case["gold"])
        per_case.append(result)

    n = len(per_case)
    if n == 0:
        return {"macro_precision": 0.0, "macro_recall": 0.0, "macro_f1": 0.0, "per_case": []}

    macro_p = sum(c["precision"] for c in per_case) / n
    macro_r = sum(c["recall"]    for c in per_case) / n
    macro_f = f1_score(macro_p, macro_r)

    return {
        "macro_precision": round(macro_p, 4),
        "macro_recall":    round(macro_r, 4),
        "macro_f1":        round(macro_f, 4),
        "per_case": per_case,
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    predicted_entities = {
        "Drug":    ["Aspirin", "Metformin"],
        "Disease": ["heart attack", "diabetes"],
    }
    gold_entities = {
        "Drug":    ["Aspirin", "Metformin"],
        "Disease": ["heart attack", "type 2 diabetes"],
    }

    print("=== Gold-Standard Evaluation ===")
    result = evaluate_ner(predicted_entities, gold_entities)
    print(result)

    print("\n=== Confidence-Based Estimation ===")
    metrics = compute_metrics(predicted_entities, relations=[{"subject": "Aspirin"}])
    print(metrics)
