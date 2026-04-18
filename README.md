# 🧬 Biomedical Text Mining

An end-to-end NLP system that reads biomedical research text and automatically extracts **named entities** (drugs, diseases, genes, symptoms, treatments) and **semantic relations** between them, complete with evaluation metrics.

---

## 📁 Project Structure

```
biomedical-text-mining/
│
├── backend/
│   ├── app.py          # Flask REST API server
│   ├── ner.py          # Named Entity Recognition (dictionary + regex)
│   ├── relation.py     # Relation extraction (trigger word + heuristics)
│   ├── evaluate.py     # Precision / Recall / F1 metrics
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx                        # Root component
│   │   ├── api.js                         # Flask API service layer
│   │   ├── index.css                      # Global styles + entity highlights
│   │   └── components/
│   │       ├── TextInput.jsx              # Input area + example shortcuts
│   │       ├── AnnotatedText.jsx          # Colour-coded entity highlights
│   │       ├── EntitiesCard.jsx           # Grouped entity tags
│   │       ├── RelationsCard.jsx          # Subject → verb → Object triples
│   │       └── MetricsCard.jsx            # Precision / Recall / F1 display
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md
```

---

## 🚀 Quick Start

### 1. Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API server starts at **http://localhost:5000**.

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

The React app starts at **http://localhost:3000** and proxies API calls to Flask.

---

## 🏗 Architecture

```
User Input (React)
      ↓
POST /analyze  →  Flask (app.py)
                      ↓
               Text Preprocessing
                      ↓
               NER (ner.py)          ← dictionary + regex patterns
                      ↓
               Relation Extraction   ← trigger words + entity-type heuristics
               (relation.py)
                      ↓
               Evaluation Metrics    ← Precision / Recall / F1
               (evaluate.py)
                      ↓
               JSON Response
                      ↓
         React UI renders results
```

---

## 📡 API Reference

### `POST /analyze`

**Request**
```json
{ "text": "Aspirin reduces risk of heart attack in patients." }
```

**Response**
```json
{
  "entities": {
    "Drug":    ["Aspirin"],
    "Disease": ["heart attack"]
  },
  "relations": [
    "Aspirin -> reduces -> heart attack"
  ],
  "highlighted_text": "<drug>Aspirin</drug> reduces risk of <disease>heart attack</disease> in patients.",
  "metrics": {
    "precision": 0.85,
    "recall":    0.78,
    "f1":        0.81,
    "entities_found": 2,
    "relations_found": 1,
    "entity_breakdown": { "Drug": 1, "Disease": 1 },
    "mode": "estimated"
  },
  "summary": "Found 2 entities: Aspirin (Drug), heart attack (Disease). Detected 1 relation."
}
```

---

## 🧠 NLP Modules

### `ner.py` — Named Entity Recognition
- **Dictionary matching**: curated lists of 500+ biomedical terms across 5 entity types
- **Regex fallback**: morphological patterns for drug suffixes (`-mab`, `-nib`, `-stat`) and gene abbreviations (`BRCA1`, `IL-6`)
- **Longest-match**: multi-word terms (e.g., "non-small cell lung cancer") match before single words

### `relation.py` — Relation Extraction
- **Trigger word patterns**: 10 relation types with regex trigger banks (`reduces`, `inhibits`, `activates`, etc.)
- **Proximity matching**: finds the closest occurrence pair of two entities, inspects the bridging text
- **Type-pair heuristics**: fallback when no trigger word is found (e.g., Drug + Disease → `treats`)

### `evaluate.py` — Evaluation
- **Gold-standard mode**: exact entity-match evaluation when ground truth annotations are provided
- **Confidence estimation**: scales benchmark baselines by per-entity-type confidence weights for real-time feedback
- **Batch evaluation**: `batch_evaluate()` for offline benchmarking across test sets

---

## 🎯 Entity Types

| Type       | Examples                                       | Color  |
|------------|------------------------------------------------|--------|
| Drug       | Aspirin, Metformin, Pembrolizumab              | Blue   |
| Disease    | Heart attack, Type 2 diabetes, Lung cancer     | Purple |
| Gene       | BRCA1, TP53, PD-1, EGFR                       | Green  |
| Symptom    | Memory loss, Insulin resistance, Chest pain    | Amber  |
| Treatment  | Chemotherapy, Immunotherapy, Surgery           | Pink   |

---

## 📊 Evaluation Metrics

| Metric    | Formula                    | Description                          |
|-----------|----------------------------|--------------------------------------|
| Precision | TP / (TP + FP)             | Of all predicted entities, how many are correct |
| Recall    | TP / (TP + FN)             | Of all true entities, how many were found |
| F1 Score  | 2·P·R / (P + R)            | Harmonic mean of Precision and Recall |

---

## ⚙ Environment Variables

Create a `.env` file in `frontend/`:
```
REACT_APP_API_URL=http://localhost:5000
```

---

## 🔬 Example End-to-End

**Input:**
```
Pembrolizumab blocks PD-1 receptor interactions and activates T-cell
responses to treat non-small cell lung cancer and melanoma.
```

**Output:**
- **Entities** → Drug: Pembrolizumab · Disease: non-small cell lung cancer, melanoma · Gene: PD-1
- **Relations** → Pembrolizumab → treats → non-small cell lung cancer · Pembrolizumab → activates → PD-1
- **Metrics** → Precision: 88% · Recall: 81% · F1: 84%
