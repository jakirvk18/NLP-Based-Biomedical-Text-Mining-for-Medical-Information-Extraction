/**
 * RelationsCard.jsx
 * Displays extracted entity relations as Subject → verb → Object triples.
 */

import React from "react";

const TYPE_COLOR = {
  Drug:      "#38bdf8",
  Disease:   "#a78bfa",
  Gene:      "#34d399",
  Symptom:   "#fbbf24",
  Treatment: "#f9a8d4",
};

function RelationPill({ label, type }) {
  const color = TYPE_COLOR[type] || "#94a3b8";
  return (
    <span
      style={{
        background: "#1e293b",
        borderRadius: 5,
        padding: "0.2rem 0.5rem",
        fontFamily: "'IBM Plex Mono', monospace",
        fontWeight: 500,
        fontSize: "0.82rem",
        color,
      }}
    >
      {label}
    </span>
  );
}

function RelationItem({ rel }) {
  // rel can be a string "A -> verb -> B" or a structured object
  if (typeof rel === "string") {
    const parts = rel.split(" -> ");
    return (
      <div
        style={{
          background: "#0a0e1a",
          borderRadius: 10,
          padding: "0.85rem 1rem",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          flexWrap: "wrap",
          fontSize: "0.82rem",
          border: "1px solid #1a2235",
        }}
      >
        {parts.map((p, i) => (
          <React.Fragment key={i}>
            {i === 1 ? (
              <span
                style={{
                  color: "#f472b6",
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: "0.75rem",
                  fontStyle: "italic",
                }}
              >
                {p}
              </span>
            ) : (
              <span
                style={{
                  background: "#1e293b",
                  borderRadius: 5,
                  padding: "0.2rem 0.5rem",
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontWeight: 500,
                  color: "#e2e8f0",
                }}
              >
                {p}
              </span>
            )}
            {i < parts.length - 1 && (
              <span style={{ color: "#334155", fontSize: 12 }}>→</span>
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  // Structured object from backend
  return (
    <div
      style={{
        background: "#0a0e1a",
        borderRadius: 10,
        padding: "0.85rem 1rem",
        display: "flex",
        alignItems: "center",
        gap: "0.5rem",
        flexWrap: "wrap",
        fontSize: "0.82rem",
        border: "1px solid #1a2235",
      }}
    >
      <RelationPill label={rel.subject} type={rel.subject_type} />
      <span style={{ color: "#334155", fontSize: 12 }}>→</span>
      <span
        style={{
          color: "#f472b6",
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: "0.75rem",
          fontStyle: "italic",
        }}
      >
        {rel.verb}
      </span>
      <span style={{ color: "#334155", fontSize: 12 }}>→</span>
      <RelationPill label={rel.object} type={rel.object_type} />
    </div>
  );
}

export default function RelationsCard({ relations }) {
  if (!relations || relations.length === 0) return null;

  return (
    <div
      className="fade-in"
      style={{
        background: "#111827",
        border: "1px solid #1e293b",
        borderRadius: 16,
        padding: "1.25rem",
        marginBottom: "1rem",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.6rem",
          marginBottom: "1rem",
          paddingBottom: "0.75rem",
          borderBottom: "1px solid #1e293b",
        }}
      >
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 8,
            background: "#2a0a1a",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 14,
          }}
        >
          🔗
        </div>
        <span
          style={{
            fontSize: "0.82rem",
            fontWeight: 700,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            fontFamily: "'IBM Plex Mono', monospace",
            color: "#f472b6",
          }}
        >
          Relations
        </span>
        <span
          style={{
            marginLeft: "auto",
            background: "#1e293b",
            borderRadius: 999,
            fontSize: "0.68rem",
            fontFamily: "'IBM Plex Mono', monospace",
            color: "#64748b",
            padding: "0.15rem 0.55rem",
          }}
        >
          {relations.length} detected
        </span>
      </div>

      {/* Relation items */}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {relations.map((rel, i) => (
          <RelationItem key={i} rel={rel} />
        ))}
      </div>
    </div>
  );
}
