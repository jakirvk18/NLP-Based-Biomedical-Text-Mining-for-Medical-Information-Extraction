/**
 * AnnotatedText.jsx
 * Renders biomedical text with highlighted entities.
 * Parses <drug>, <disease>, <gene>, <symptom>, <treatment> tags.
 */

import React, { useMemo } from "react";

const ENTITY_TAGS = ["drug", "disease", "gene", "symptom", "treatment"];

const LEGEND = [
  { tag: "drug", label: "Drug", color: "#38bdf8" },
  { tag: "disease", label: "Disease", color: "#a78bfa" },
  { tag: "gene", label: "Gene", color: "#34d399" },
  { tag: "symptom", label: "Symptom", color: "#fbbf24" },
  { tag: "treatment", label: "Treatment", color: "#f9a8d4" },
];

/**
 * Converts tagged HTML-like string into renderable parts
 */
function parseHighlightedText(text) {
  if (!text) return [];

  const pattern = new RegExp(
    `<(${ENTITY_TAGS.join("|")})>(.*?)</\\1>`,
    "gi"
  );

  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    const [fullMatch, tag, content] = match;
    const index = match.index;

    // push plain text before match
    if (index > lastIndex) {
      parts.push({
        type: "text",
        value: text.slice(lastIndex, index),
      });
    }

    // push entity
    parts.push({
      type: "entity",
      tag: tag.toLowerCase(),
      value: content,
    });

    lastIndex = index + fullMatch.length;
  }

  // push remaining text
  if (lastIndex < text.length) {
    parts.push({
      type: "text",
      value: text.slice(lastIndex),
    });
  }

  return parts;
}

export default function AnnotatedText({ highlightedText }) {
  const parts = useMemo(
    () => parseHighlightedText(highlightedText),
    [highlightedText]
  );

  if (!highlightedText) return null;

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
            background: "#0f2942",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 14,
          }}
        >
          📄
        </div>

        <span
          style={{
            fontSize: "0.82rem",
            fontWeight: 700,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            fontFamily: "'IBM Plex Mono', monospace",
            color: "#38bdf8",
          }}
        >
          Annotated Text
        </span>
      </div>

      {/* Highlighted Text */}
      <div
        style={{
          background: "#0a0e1a",
          borderRadius: 10,
          padding: "1rem",
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: "0.85rem",
          lineHeight: 1.8,
          border: "1px solid #1e293b",
        }}
      >
        {parts.map((part, i) =>
          part.type === "text" ? (
            <span key={i}>{part.value}</span>
          ) : (
            <span key={i} className={`hl-${part.tag}`}>
              {part.value}
            </span>
          )
        )}
      </div>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          marginTop: "0.75rem",
        }}
      >
        {LEGEND.map((item) => (
          <div
            key={item.tag}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.3rem",
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: 2,
                background: item.color,
              }}
            />
            <span
              style={{
                fontSize: "0.68rem",
                color: "#64748b",
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            >
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}