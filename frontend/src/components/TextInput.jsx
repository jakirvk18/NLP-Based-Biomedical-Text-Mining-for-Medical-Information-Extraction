/**
 * TextInput.jsx
 * Biomedical text input area with example sentence shortcuts.
 */

import React from "react";

const EXAMPLES = [
  {
    label: "Aspirin & heart attack",
    text: "Aspirin reduces the risk of heart attack in patients with cardiovascular disease. Clinical trials have shown that low-dose aspirin therapy significantly lowers platelet aggregation and prevents thrombosis in high-risk patients.",
  },
  {
    label: "Metformin & diabetes",
    text: "Metformin controls blood sugar levels in type 2 diabetes patients by reducing insulin resistance. Recent studies indicate that metformin also demonstrates anti-inflammatory properties and may reduce the risk of colorectal cancer.",
  },
  {
    label: "Cancer immunotherapy",
    text: "Pembrolizumab, an anti-PD-1 antibody, has shown significant efficacy in treating non-small cell lung cancer and melanoma. The drug activates T-cell responses by blocking PD-1 receptor interactions with PD-L1 ligands expressed on tumor cells.",
  },
  {
    label: "Alzheimer's treatment",
    text: "Donepezil and memantine are commonly used to treat Alzheimer's disease symptoms including memory loss and cognitive decline. These drugs modulate acetylcholinesterase activity and NMDA receptor function respectively to slow neurodegeneration.",
  },
];

export default function TextInput({ value, onChange, onAnalyze, loading }) {
  return (
    <div
      style={{
        background: "#111827",
        border: "1px solid #1e293b",
        borderRadius: 16,
        padding: "1.5rem",
        marginBottom: "1.5rem",
      }}
    >
      {/* Label */}
      <label
        style={{
          display: "block",
          fontSize: "0.7rem",
          color: "#64748b",
          fontFamily: "'IBM Plex Mono', monospace",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          marginBottom: "0.5rem",
        }}
      >
        Biomedical Research Text
      </label>

      {/* Textarea */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={"Paste a biomedical paragraph here...\n\nExample: Metformin controls blood sugar in diabetes patients."}
        rows={6}
        style={{
          width: "100%",
          background: "#0a0e1a",
          border: "1px solid #1e293b",
          borderRadius: 10,
          color: "#e2e8f0",
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: "0.85rem",
          padding: "0.9rem",
          resize: "vertical",
          lineHeight: 1.7,
          outline: "none",
          transition: "border-color 0.2s",
        }}
        onFocus={(e) => (e.target.style.borderColor = "#38bdf8")}
        onBlur={(e) => (e.target.style.borderColor = "#1e293b")}
      />

      {/* Character count */}
      <div
        style={{
          fontSize: "0.68rem",
          color: "#475569",
          fontFamily: "'IBM Plex Mono', monospace",
          textAlign: "right",
          marginTop: "0.3rem",
        }}
      >
        {value.length} / 5000 characters
      </div>

      {/* Example shortcuts */}
      <div style={{ marginTop: "0.75rem" }}>
        <span
          style={{
            fontSize: "0.68rem",
            color: "#475569",
            fontFamily: "'IBM Plex Mono', monospace",
            marginRight: "0.5rem",
          }}
        >
          Try:
        </span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex.label}
            onClick={() => onChange(ex.text)}
            style={{
              background: "#1e293b",
              border: "1px solid #334155",
              borderRadius: 8,
              color: "#94a3b8",
              fontSize: "0.72rem",
              fontFamily: "'IBM Plex Mono', monospace",
              padding: "0.3rem 0.6rem",
              marginRight: "0.4rem",
              marginBottom: "0.4rem",
              cursor: "pointer",
              transition: "all 0.15s",
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = "#38bdf8";
              e.target.style.color = "#38bdf8";
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = "#334155";
              e.target.style.color = "#94a3b8";
            }}
          >
            {ex.label}
          </button>
        ))}
      </div>

      {/* Analyze button */}
      <button
        onClick={onAnalyze}
        disabled={loading || !value.trim()}
        style={{
          width: "100%",
          marginTop: "1rem",
          padding: "0.85rem",
          background: loading
            ? "#1e293b"
            : "linear-gradient(135deg, #0ea5e9, #6366f1)",
          border: "none",
          borderRadius: 10,
          color: loading ? "#64748b" : "#fff",
          fontFamily: "'Syne', sans-serif",
          fontSize: "0.95rem",
          fontWeight: 700,
          cursor: loading || !value.trim() ? "not-allowed" : "pointer",
          letterSpacing: "0.02em",
          transition: "opacity 0.2s",
          opacity: !value.trim() ? 0.5 : 1,
        }}
      >
        {loading ? "Analyzing…" : "Analyze Text"}
      </button>
    </div>
  );
}
