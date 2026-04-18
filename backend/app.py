"""
Biomedical Text Mining - Flask Backend
Main API server with CORS support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from ner import extract_entities
from relation import extract_relations
from evaluate import compute_metrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow React frontend to call this API


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Biomedical Text Mining API"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main endpoint: receives biomedical text, returns entities + relations + metrics.

    Request body:
        { "text": "Aspirin reduces heart attack risk in patients." }

    Response:
        {
            "entities": { "Drug": [...], "Disease": [...], ... },
            "relations": [ "Drug -> verb -> Disease", ... ],
            "highlighted_text": "...",
            "metrics": { "precision": 0.9, "recall": 0.85, "f1": 0.87, ... }
        }
    """
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text cannot be empty"}), 400

    if len(text) > 5000:
        return jsonify({"error": "Text too long. Maximum 5000 characters."}), 400

    logger.info(f"Analyzing text ({len(text)} chars)...")

    # Step 1: Extract named entities (NER)
    entities = extract_entities(text)
    logger.info(f"Entities found: {sum(len(v) for v in entities.items())}")

    # Step 2: Extract relations between entities
    relations, relation_objects = extract_relations(text, entities)
    logger.info(f"Relations found: {len(relations)}")

    # Step 3: Generate highlighted HTML text
    highlighted = build_highlighted_text(text, entities)

    # Step 4: Compute evaluation metrics
    metrics = compute_metrics(entities, relation_objects)

    return jsonify({
        "entities": entities,
        "relations": relations,
        "highlighted_text": highlighted,
        "metrics": metrics,
        "summary": build_summary(entities, relations)
    })


def build_highlighted_text(text: str, entities: dict) -> str:
    """Wraps recognized entities in HTML-style tags for frontend highlighting."""
    # Collect all (start, end, type, surface) spans
    spans = []
    text_lower = text.lower()

    tag_map = {
        "Drug": "drug",
        "Disease": "disease",
        "Gene": "gene",
        "Symptom": "symptom",
        "Treatment": "treatment"
    }

    for entity_type, entity_list in entities.items():
        tag = tag_map.get(entity_type, "other")
        for entity in entity_list:
            start = text_lower.find(entity.lower())
            while start != -1:
                end = start + len(entity)
                spans.append((start, end, tag, text[start:end]))
                start = text_lower.find(entity.lower(), end)

    # Sort by start position, remove overlaps
    spans.sort(key=lambda x: x[0])
    filtered = []
    last_end = 0
    for span in spans:
        if span[0] >= last_end:
            filtered.append(span)
            last_end = span[1]

    # Build highlighted string
    result = ""
    cursor = 0
    for start, end, tag, surface in filtered:
        result += text[cursor:start]
        result += f"<{tag}>{surface}</{tag}>"
        cursor = end
    result += text[cursor:]
    return result


def build_summary(entities: dict, relations: list) -> str:
    all_entities = []
    for etype, elist in entities.items():
        for e in elist:
            all_entities.append(f"{e} ({etype})")

    if not all_entities:
        return "No biomedical entities detected in this text."

    summary = f"Found {len(all_entities)} entit{'y' if len(all_entities)==1 else 'ies'}"
    if all_entities:
        summary += f": {', '.join(all_entities[:4])}"
        if len(all_entities) > 4:
            summary += f" and {len(all_entities)-4} more"
    if relations:
        summary += f". Detected {len(relations)} relation{'s' if len(relations)>1 else ''}."
    return summary


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
