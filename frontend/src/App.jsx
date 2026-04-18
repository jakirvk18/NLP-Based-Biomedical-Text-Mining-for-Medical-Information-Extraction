/**
 * App.jsx
 * Root component for Biomedical Text Mining UI
 */

import React, { useState, useCallback } from "react";
import TextInput from "./components/TextInput";
import AnnotatedText from "./components/AnnotatedText";
import EntitiesCard from "./components/EntitiesCard";
import RelationsCard from "./components/RelationsCard";
import MetricsCard from "./components/MetricsCard";
import { analyzeText } from "./api";

/* ---------------------------
   Helpers
---------------------------- */

function formatEntities(entityList) {
  if (!Array.isArray(entityList)) return entityList;

  const grouped = {};

  entityList.forEach((e) => {
    if (!grouped[e.label]) {
      grouped[e.label] = [];
    }
    grouped[e.label].push(e.text);
  });

  return grouped;
}

function formatRelations(relations = []) {
  return relations.map((r) => {
    // If already structured object
    if (typeof r === "object") {
      return {
        subject: r.subject,
        verb: r.relation || r.verb,
        object: r.object,
        subject_type: r.subject_type || "",
        object_type: r.object_type || "",
      };
    }

    // If string "A -> verb -> B"
    if (typeof r === "string") {
      const parts = r.split(" -> ");
      return {
        subject: parts[0],
        verb: parts[1],
        object: parts[2],
        subject_type: "",
        object_type: "",
      };
    }

    return r;
  });
}

/* ---------------------------
   Component
---------------------------- */

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = useCallback(async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzeText(text);
      setResult(data);
    } catch (err) {
      setError(err?.message || "Unexpected server error");
    } finally {
      setLoading(false);
    }
  }, [text]);

  const formattedEntities = result
  ? formatEntities(result.entities) || {}
  : {};

  const formattedRelations = result
  ? formatRelations(result.relations || [])
  : [];
  console.log("RESULT:", result);
  return (
    <div
      style={{
        maxWidth: 880,
        margin: "0 auto",
        padding: "2rem 1.25rem",
        minHeight: "100vh",
      }}
    >
      {/* Header */}
      <header style={{ textAlign: "center", marginBottom: "2rem" }}>
        <div
          style={{
            display: "inline-block",
            background: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 999,
            fontSize: "0.7rem",
            padding: "0.2rem 0.75rem",
            color: "#94a3b8",
            fontFamily: "'IBM Plex Mono', monospace",
            marginBottom: "0.9rem",
          }}
        >
          NLP · NER · Relation Extraction · F1 Evaluation
        </div>

        <h1
          style={{
            fontSize: "clamp(1.6rem, 5vw, 2.2rem)",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            background:
              "linear-gradient(135deg, #38bdf8, #818cf8, #f472b6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            margin: "0 0 0.4rem",
          }}
        >
          Biomedical Text Mining
        </h1>

        <p
          style={{
            color: "#64748b",
            fontSize: "0.875rem",
            fontFamily: "'IBM Plex Mono', monospace",
          }}
        >
          Extract entities & relations from medical research text using NLP
        </p>
      </header>

      {/* Input */}
      <TextInput
        value={text}
        onChange={setText}
        onAnalyze={handleAnalyze}
        loading={loading}
      />

      {/* Loading */}
      {loading && (
        <div
          className="pulse"
          style={{
            textAlign: "center",
            padding: "2rem",
            color: "#64748b",
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: "0.82rem",
          }}
        >
          Running NLP pipeline · Extracting entities · Detecting relations…
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            background: "#1a0a0a",
            border: "1px solid #7f1d1d",
            borderRadius: 10,
            padding: "1rem",
            color: "#fca5a5",
            fontSize: "0.82rem",
            fontFamily: "'IBM Plex Mono', monospace",
            marginBottom: "1rem",
          }}
        >
          ⚠ {error}
        </div>
      )}

      {/* Results */}
      {result && !loading && (
  <>
    <AnnotatedText highlightedText={result.highlighted_text} />

    <EntitiesCard entities={formattedEntities || {}} />

    <RelationsCard relations={formattedRelations || []} />

    <MetricsCard
      metrics={result.metrics || {}}
      summary={result.summary}
    />
  </>
)}

      {/* Footer */}
      <footer
        style={{
          textAlign: "center",
          marginTop: "2rem",
          paddingTop: "1.5rem",
          borderTop: "1px solid #1e293b",
          color: "#334155",
          fontSize: "0.72rem",
          fontFamily: "'IBM Plex Mono', monospace",
        }}
      >
        Designed and developed by Jakir Hussain
      </footer>
    </div>
  );
}