"""
Biomedical Relation Extraction Module

Detects semantic relations between biomedical entities using:
  1. Dependency-style pattern matching on verb phrases between entities
  2. Proximity-based co-occurrence with trigger words
  3. Template-based triple generation: Subject → Verb → Object

Relation types detected:
  - TREATS            : drug treats disease
  - CAUSES            : entity causes disease/symptom
  - INHIBITS          : drug inhibits gene/pathway
  - ACTIVATES         : drug/entity activates gene/pathway
  - REDUCES           : entity reduces symptom/risk
  - CONTROLS          : drug controls disease
  - ASSOCIATED_WITH   : entity associated with disease
  - INTERACTS_WITH    : drug-drug or drug-gene interaction
  - EXPRESSES         : gene expressed in condition
  - PREVENTS          : entity prevents disease
"""

import re
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Trigger word banks for each relation type
# ---------------------------------------------------------------------------

RELATION_TRIGGERS = {
    "treats": [
        r"\btreats?\b", r"\bused to treat\b", r"\btherapy for\b",
        r"\bmanages?\b", r"\bprescribed for\b", r"\bindicates?\b",
    ],
    "reduces": [
        r"\breduces?\b", r"\blowers?\b", r"\bdecrease[sd]?\b",
        r"\battenuates?\b", r"\bmitigates?\b", r"\blessens?\b",
        r"\bdimin[i]?shes?\b",
    ],
    "inhibits": [
        r"\binhibits?\b", r"\bblocks?\b", r"\bsuppresses?\b",
        r"\bantagonizes?\b", r"\bprevents?\b", r"\bimpairs?\b",
    ],
    "activates": [
        r"\bactivates?\b", r"\bstimulates?\b", r"\bupregulates?\b",
        r"\benhances?\b", r"\binduces?\b", r"\bpromotes?\b",
    ],
    "causes": [
        r"\bcauses?\b", r"\binduces?\b", r"\btriggers?\b",
        r"\bproduces?\b", r"\bincreases? risk of\b", r"\bleads? to\b",
    ],
    "controls": [
        r"\bcontrols?\b", r"\bregulates?\b", r"\bmodulates?\b",
        r"\bmanages?\b", r"\bstabilizes?\b",
    ],
    "associated_with": [
        r"\bassociated with\b", r"\blinked to\b", r"\bcorrelates? with\b",
        r"\bconnected to\b", r"\brelated to\b", r"\bimplicated in\b",
    ],
    "interacts_with": [
        r"\binteracts? with\b", r"\bbinds? to\b", r"\btargets?\b",
        r"\bacts on\b", r"\bengages?\b",
    ],
    "prevents": [
        r"\bprevents?\b", r"\bprotects? against\b", r"\bprophylaxis\b",
        r"\bwards? off\b",
    ],
    "expresses": [
        r"\bexpresse[sd]?\b", r"\boverexpressen?\b", r"\bproduces?\b",
        r"\bsecretes?\b",
    ],
}

# Human-readable label for each relation key
RELATION_LABEL = {
    "treats": "treats",
    "reduces": "reduces",
    "inhibits": "inhibits",
    "activates": "activates",
    "causes": "causes",
    "controls": "controls",
    "associated_with": "associated with",
    "interacts_with": "interacts with",
    "prevents": "prevents",
    "expresses": "expresses",
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _find_offsets(text: str, entity: str) -> List[Tuple[int, int]]:
    """Return all (start, end) character offsets of entity in text (case-insensitive)."""
    offsets = []
    lower_text = text.lower()
    lower_entity = entity.lower()
    start = 0
    while True:
        idx = lower_text.find(lower_entity, start)
        if idx == -1:
            break
        offsets.append((idx, idx + len(entity)))
        start = idx + 1
    return offsets


def _window_between(text: str, start1: int, end1: int, start2: int, end2: int,
                    max_chars: int = 120) -> str:
    """
    Extract the text substring between two entity spans.
    Returns empty string if the gap exceeds max_chars.
    """
    left_end = min(end1, end2)
    right_start = max(start1, start2)

    if right_start <= left_end:
        # Overlapping or adjacent – use a small surrounding window
        return text[max(0, left_end - 5): right_start + 5]

    gap = text[left_end:right_start]
    if len(gap) > max_chars:
        return ""
    return gap


def _detect_relation_in_window(window: str) -> str:
    """
    Check trigger patterns against the text window between two entities.
    Returns the matched relation key, or "" if none.
    """
    window_lower = window.lower()
    for rel_key, patterns in RELATION_TRIGGERS.items():
        for pat in patterns:
            if re.search(pat, window_lower):
                return rel_key
    return ""


# ---------------------------------------------------------------------------
# Core relation extraction
# ---------------------------------------------------------------------------

RelationObject = Dict[str, str]  # { subject, subject_type, verb, object, object_type }


def _split_sentences(text: str) -> List[str]:
    """Simple sentence splitter on '.', '!', '?' boundaries."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def extract_relations(
    text: str,
    entities: Dict[str, List[str]],
    max_window: int = 80,        # tighter window = fewer spurious pairs
) -> Tuple[List[str], List[RelationObject]]:
    """
    Extract relations between pairs of entities.

    Algorithm:
      For every pair of entity mentions (different types):
        1. Find all occurrence offsets of each entity in text.
        2. For the closest pair of occurrences, extract the bridging text.
        3. Search the bridge for trigger words.
        4. If found, record the triple (subject, relation, object).

    Returns:
        relations  : human-readable strings  ["Aspirin -> reduces -> heart attack"]
        rel_objects: structured dicts for the frontend and metrics
    """
    # Flatten to list of (surface_form, entity_type)
    all_entities: List[Tuple[str, str]] = []
    for etype, elist in entities.items():
        for e in elist:
            all_entities.append((e, etype))

    relations: List[str] = []
    rel_objects: List[RelationObject] = []
    seen_triples: set = set()

    # Work sentence-by-sentence to avoid cross-sentence spurious pairs
    sentences = _split_sentences(text)

    for i, (ent_a, type_a) in enumerate(all_entities):
        for j, (ent_b, type_b) in enumerate(all_entities):
            if i >= j:
                continue

            # Only consider pairs that co-occur in the same sentence
            shared_sentences = [
                s for s in sentences
                if ent_a.lower() in s.lower() and ent_b.lower() in s.lower()
            ]
            if not shared_sentences:
                continue

            # Use the first shared sentence as the search context
            sentence = shared_sentences[0]

            offsets_a = _find_offsets(sentence, ent_a)
            offsets_b = _find_offsets(sentence, ent_b)

            if not offsets_a or not offsets_b:
                continue

            # Find the closest pair of occurrences within the sentence
            best_dist = float("inf")
            best_a_span = offsets_a[0]
            best_b_span = offsets_b[0]

            for sa, ea in offsets_a:
                for sb, eb in offsets_b:
                    dist = abs(sa - sb)
                    if dist < best_dist:
                        best_dist = dist
                        best_a_span = (sa, ea)
                        best_b_span = (sb, eb)

            window = _window_between(
                sentence,
                best_a_span[0], best_a_span[1],
                best_b_span[0], best_b_span[1],
                max_chars=max_window,
            )

            if not window:
                continue

            rel_key = _detect_relation_in_window(window)

            if not rel_key:
                # Try sentence-level context when no trigger found in gap
                rel_key = _infer_relation_by_type(type_a, type_b)

            if not rel_key:
                continue

            # Determine subject / object ordering by position in text
            if best_a_span[0] <= best_b_span[0]:
                subject, subj_type = ent_a, type_a
                obj, obj_type = ent_b, type_b
            else:
                subject, subj_type = ent_b, type_b
                obj, obj_type = ent_a, type_a

            # Capitalise surface forms nicely
            subject = subject.capitalize()
            obj_surface = obj.capitalize() if len(obj) > 3 else obj

            triple_key = (subject.lower(), rel_key, obj_surface.lower())
            if triple_key in seen_triples:
                continue
            seen_triples.add(triple_key)

            verb_label = RELATION_LABEL[rel_key]
            rel_str = f"{subject} -> {verb_label} -> {obj_surface}"
            relations.append(rel_str)
            rel_objects.append({
                "subject": subject,
                "subject_type": subj_type,
                "verb": verb_label,
                "object": obj_surface,
                "object_type": obj_type,
            })

    return relations, rel_objects


def _infer_relation_by_type(type_a: str, type_b: str) -> str:
    """
    Fallback: infer a likely relation from entity-type pair alone
    when no explicit trigger word was found in the window.
    """
    pair = frozenset([type_a, type_b])

    if pair == frozenset(["Drug", "Disease"]):
        return "treats"
    if pair == frozenset(["Drug", "Gene"]):
        return "inhibits"
    if pair == frozenset(["Drug", "Symptom"]):
        return "reduces"
    if pair == frozenset(["Gene", "Disease"]):
        return "associated_with"
    if pair == frozenset(["Disease", "Symptom"]):
        return "associated_with"
    if pair == frozenset(["Treatment", "Disease"]):
        return "treats"
    if pair == frozenset(["Drug", "Treatment"]):
        return "interacts_with"

    return ""


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from ner import extract_entities

    sample = (
        "Pembrolizumab, an anti-PD-1 antibody, blocks PD-L1 interactions and activates "
        "T-cell responses to treat non-small cell lung cancer and melanoma. "
        "Metformin reduces insulin resistance in type 2 diabetes patients."
    )
    entities = extract_entities(sample)
    print("Entities:", entities)

    rels, rel_objs = extract_relations(sample, entities)
    print("\nRelations:")
    for r in rels:
        print(" ", r)
