"""
Biomedical NER (Named Entity Recognition) Module

Uses a two-layer approach:
  1. Rule-based matching against curated biomedical dictionaries
  2. Pattern-based extraction for unknown entities using regex heuristics

Entity types:
  - Drug       : pharmaceutical agents, medications
  - Disease    : diseases, conditions, disorders, syndromes
  - Gene       : genes, proteins, receptors, enzymes
  - Symptom    : clinical symptoms, signs
  - Treatment  : procedures, therapies, interventions
"""

import re
import string
from typing import Dict, List


# ---------------------------------------------------------------------------
# Curated Biomedical Dictionaries
# ---------------------------------------------------------------------------

DRUG_DICT = {
    # NSAIDs
    "aspirin", "ibuprofen", "naproxen", "diclofenac", "celecoxib", "indomethacin",
    # Antibiotics
    "amoxicillin", "penicillin", "ciprofloxacin", "azithromycin", "doxycycline",
    "vancomycin", "metronidazole", "clindamycin", "erythromycin", "ampicillin",
    # Antidiabetics
    "metformin", "insulin", "glipizide", "glyburide", "sitagliptin", "empagliflozin",
    "liraglutide", "pioglitazone", "rosiglitazone", "canagliflozin",
    # Cardiovascular
    "atorvastatin", "simvastatin", "lisinopril", "losartan", "amlodipine",
    "metoprolol", "warfarin", "clopidogrel", "digoxin", "furosemide", "spironolactone",
    # Oncology / Immunology
    "pembrolizumab", "nivolumab", "trastuzumab", "rituximab", "bevacizumab",
    "imatinib", "erlotinib", "gefitinib", "tamoxifen", "paclitaxel", "docetaxel",
    "cisplatin", "carboplatin", "doxorubicin", "cyclophosphamide", "vincristine",
    # Neurology / Psychiatry
    "donepezil", "memantine", "levodopa", "carbidopa", "haloperidol", "olanzapine",
    "risperidone", "quetiapine", "sertraline", "fluoxetine", "escitalopram",
    "paroxetine", "venlafaxine", "duloxetine", "lithium", "valproate", "lamotrigine",
    "gabapentin", "pregabalin", "phenytoin", "carbamazepine",
    # Steroids / Anti-inflammatory
    "prednisone", "prednisolone", "dexamethasone", "hydrocortisone", "methylprednisolone",
    "betamethasone", "triamcinolone",
    # Antivirals / Antiparasitics
    "remdesivir", "oseltamivir", "acyclovir", "valacyclovir", "tenofovir",
    "efavirenz", "lopinavir", "ritonavir", "ivermectin", "chloroquine", "hydroxychloroquine",
    # Other
    "omeprazole", "pantoprazole", "ranitidine", "albuterol", "salbutamol",
    "montelukast", "cetirizine", "loratadine", "diphenhydramine", "acetaminophen",
    "paracetamol", "morphine", "oxycodone", "tramadol", "naloxone", "naltrexone",
}

DISEASE_DICT = {
    # Cardiovascular
    "heart attack", "myocardial infarction", "stroke", "hypertension", "hypotension",
    "heart failure", "atrial fibrillation", "coronary artery disease", "atherosclerosis",
    "angina", "thrombosis", "embolism", "pulmonary embolism", "deep vein thrombosis",
    # Metabolic
    "diabetes", "type 2 diabetes", "type 1 diabetes", "obesity", "hyperlipidemia",
    "hypercholesterolemia", "metabolic syndrome", "hypothyroidism", "hyperthyroidism",
    # Cancer
    "cancer", "lung cancer", "breast cancer", "colorectal cancer", "prostate cancer",
    "leukemia", "lymphoma", "melanoma", "glioblastoma", "carcinoma", "sarcoma",
    "non-small cell lung cancer", "hepatocellular carcinoma", "pancreatic cancer",
    # Neurological
    "alzheimer's disease", "alzheimer's", "parkinson's disease", "parkinson's",
    "multiple sclerosis", "epilepsy", "dementia", "depression", "anxiety",
    "schizophrenia", "bipolar disorder", "autism", "adhd", "migraine",
    # Infectious
    "covid-19", "influenza", "pneumonia", "tuberculosis", "hiv", "aids",
    "hepatitis", "hepatitis b", "hepatitis c", "malaria", "sepsis",
    # Autoimmune / Inflammatory
    "rheumatoid arthritis", "arthritis", "lupus", "psoriasis", "inflammatory bowel disease",
    "crohn's disease", "ulcerative colitis", "multiple sclerosis", "celiac disease",
    # Respiratory
    "asthma", "copd", "chronic obstructive pulmonary disease", "bronchitis", "emphysema",
    # Renal / GI
    "kidney disease", "chronic kidney disease", "renal failure", "cirrhosis",
    "fatty liver disease", "pancreatitis", "gastritis", "peptic ulcer",
    # Other
    "osteoporosis", "anemia", "fibromyalgia",
}

GENE_DICT = {
    # Tumour suppressors / Oncogenes
    "brca1", "brca2", "tp53", "p53", "kras", "ras", "egfr", "her2", "erbb2",
    "apc", "vegf", "vegfr", "alk", "braf", "met", "myc", "c-myc", "mdm2",
    "rb1", "cdkn2a", "pten", "nf1", "vhl", "ret", "kit", "pdgfr",
    # Receptors / Signalling
    "pd-1", "pd-l1", "ctla-4", "tnf", "tnf-alpha", "il-6", "il-1b", "il-2",
    "il-10", "tgf-beta", "nfkb", "pi3k", "akt", "mtor", "stat3", "jak2",
    # Enzymes
    "ace", "ace2", "cox-1", "cox-2", "cyclooxygenase", "ace2", "ace",
    "acetylcholinesterase", "mao", "cyp3a4", "cyp2d6",
    # Neurological
    "app", "apoe", "apoe4", "snca", "lrrk2", "park2", "mapt", "tau",
    "amyloid", "alpha-synuclein",
    # Metabolic
    "insulin receptor", "glut4", "adiponectin", "leptin", "ghrelin",
    # Other
    "ace", "renin", "angiotensin", "aldosterone",
    "nmda receptor", "gaba receptor", "dopamine receptor",
}

SYMPTOM_DICT = {
    "fever", "cough", "fatigue", "nausea", "vomiting", "diarrhea", "headache",
    "dizziness", "shortness of breath", "dyspnea", "chest pain", "back pain",
    "abdominal pain", "joint pain", "muscle pain", "myalgia", "arthralgia",
    "memory loss", "cognitive decline", "confusion", "depression", "anxiety",
    "insomnia", "weight loss", "weight gain", "loss of appetite", "anorexia",
    "rash", "itching", "edema", "swelling", "bleeding", "bruising",
    "palpitations", "tachycardia", "bradycardia", "hypotension", "hypertension",
    "tremor", "seizure", "paralysis", "weakness", "numbness", "tingling",
    "vision loss", "blurred vision", "hearing loss", "tinnitus",
    "pallor", "jaundice", "cyanosis",
    "insulin resistance", "platelet aggregation",
}

TREATMENT_DICT = {
    "surgery", "chemotherapy", "radiation therapy", "radiotherapy",
    "immunotherapy", "targeted therapy", "hormone therapy", "stem cell transplant",
    "bone marrow transplant", "organ transplant", "dialysis", "hemodialysis",
    "physical therapy", "physiotherapy", "cognitive behavioral therapy", "cbt",
    "psychotherapy", "electroconvulsive therapy", "ect",
    "vaccination", "vaccine", "immunization",
    "blood transfusion", "plasmapheresis",
    "angioplasty", "bypass surgery", "coronary bypass",
    "stenting", "stent placement",
    "endoscopy", "colonoscopy", "biopsy",
    "mechanical ventilation", "oxygen therapy",
    "low-dose aspirin therapy",
}


# ---------------------------------------------------------------------------
# Regex patterns for unknown entities not in dictionaries
# ---------------------------------------------------------------------------

DRUG_PATTERNS = [
    r"\b[A-Z][a-z]+(?:mab|nib|tide|vir|stat|pril|artan|oxacin|mycin|cillin|azole)\b",
    r"\b[A-Z][a-z]+(?:ine|anol|olol|ipine|tidine)\b",
]

GENE_PATTERNS = [
    r"\b[A-Z]{2,6}-\d+\b",             # e.g. IL-6, IL-10 (must have digit after dash)
    r"\b[A-Z]{2,6}\d+\b",              # e.g. BRCA1, TP53
    r"\b[A-Z][a-z]+\d+\b",             # e.g. Smad3, Jak2
]


# ---------------------------------------------------------------------------
# Core NER functions
# ---------------------------------------------------------------------------

def preprocess(text: str) -> str:
    """Normalize whitespace; preserve original case for surface forms."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def dictionary_match(text: str, dictionary: set) -> List[str]:
    """
    Case-insensitive longest-match lookup against a dictionary.
    Returns deduplicated list of matched surface forms (original case).
    """
    text_lower = text.lower()
    found = []
    seen = set()

    # Sort by length desc so longer multi-word terms match first
    for term in sorted(dictionary, key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
        for m in re.finditer(pattern, text_lower):
            surface = text[m.start():m.end()]
            key = surface.lower()
            if key not in seen:
                seen.add(key)
                found.append(surface)

    return found


def pattern_match(text: str, patterns: List[str], known: List[str]) -> List[str]:
    """
    Apply regex patterns to catch entities not in the static dictionary.
    Filters out already-found known entities and common English words.
    """
    known_lower = {k.lower() for k in known}
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "are", "has", "have",
        "was", "were", "been", "being", "also", "which", "their", "they", "but",
        "not", "can", "may", "its", "into", "than", "more", "some", "when",
    }
    found = []
    seen = set()

    for pat in patterns:
        for m in re.finditer(pat, text):
            surface = m.group(0)
            key = surface.lower()
            if key not in known_lower and key not in stopwords and key not in seen:
                seen.add(key)
                found.append(surface)

    return found


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Main NER function. Applies dictionary + pattern matching to extract:
      Drug, Disease, Gene, Symptom, Treatment

    Returns:
        dict with entity type as key and list of unique surface forms as value.
        Empty lists are omitted.
    """
    text = preprocess(text)

    drugs     = dictionary_match(text, DRUG_DICT)
    diseases  = dictionary_match(text, DISEASE_DICT)
    genes     = dictionary_match(text, GENE_DICT)
    symptoms  = dictionary_match(text, SYMPTOM_DICT)
    treatments = dictionary_match(text, TREATMENT_DICT)

    # Pattern-based fallback for drugs and genes
    extra_drugs = pattern_match(text, DRUG_PATTERNS, drugs)
    extra_genes = pattern_match(text, GENE_PATTERNS, genes + drugs + diseases)

    drugs += extra_drugs
    genes += extra_genes

    # Remove cross-type overlaps (prefer more specific category)
    disease_lower = {d.lower() for d in diseases}
    symptoms = [s for s in symptoms if s.lower() not in disease_lower]

    entities = {}
    for key, lst in [("Drug", drugs), ("Disease", diseases), ("Gene", genes),
                     ("Symptom", symptoms), ("Treatment", treatments)]:
        if lst:
            # Preserve insertion order while deduplicating
            seen = set()
            deduped = []
            for item in lst:
                if item.lower() not in seen:
                    seen.add(item.lower())
                    deduped.append(item)
            entities[key] = deduped

    return entities


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = (
        "Aspirin reduces the risk of heart attack in patients with cardiovascular disease. "
        "Metformin controls blood sugar in type 2 diabetes patients by reducing insulin resistance."
    )
    result = extract_entities(sample)
    for etype, elist in result.items():
        print(f"{etype}: {elist}")
