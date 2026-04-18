import React from "react";

/* Entity type styling */
const ENTITY_TYPES = {
  Drug:      { icon: "💊", color: "#38bdf8", bg: "#0f2942", border: "#0ea5e9" },
  Disease:   { icon: "🧬", color: "#a78bfa", bg: "#2a1040", border: "#818cf8" },
  Gene:      { icon: "🔬", color: "#34d399", bg: "#0a2a1a", border: "#10b981" },
  Symptom:   { icon: "⚠",  color: "#fbbf24", bg: "#2a1a00", border: "#f59e0b" },
  Treatment: { icon: "💉", color: "#f9a8d4", bg: "#2a0a1a", border: "#f472b6" },
};

/* Individual tag */
function Tag({ text, style }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "0.25rem 0.55rem",
        margin: "0.2rem",
        borderRadius: 6,
        fontSize: "0.78rem",
        fontFamily: "'IBM Plex Mono', monospace",
        border: `1px solid ${style.border}`,
        background: style.bg,
        color: style.color,
      }}
    >
      {text}
    </span>
  );
}

/* Group section */
function Group({ title, items, style }) {
  if (!items?.length) return null;

  return (
    <div
      style={{
        background: "#0a0e1a",
        borderRadius: 10,
        padding: "0.85rem",
      }}
    >
      <div
        style={{
          marginBottom: "0.5rem",
          fontSize: "0.65rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          fontFamily: "'IBM Plex Mono', monospace",
          color: style.color,
        }}
      >
        {style.icon} {title}
      </div>

      <div>
        {items.map((item, i) => (
          <Tag key={i} text={item} style={style} />
        ))}
      </div>
    </div>
  );
}

export default function EntitiesCard({ entities = {} }) {
  const total = Object.keys(ENTITY_TYPES).reduce(
    (sum, key) => sum + (entities[key]?.length || 0),
    0
  );

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
            background: "#2a1040",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          🧬
        </div>

        <span
          style={{
            fontSize: "0.82rem",
            fontWeight: 700,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            fontFamily: "'IBM Plex Mono', monospace",
            color: "#a78bfa",
          }}
        >
          Named Entities
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
          {total} found
        </span>
      </div>

      {/* Content */}
      {total > 0 ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
            gap: "0.75rem",
          }}
        >
          {Object.entries(ENTITY_TYPES).map(([key, style]) => (
            <Group
              key={key}
              title={key}
              items={entities[key]}
              style={style}
            />
          ))}
        </div>
      ) : (
        <p
          style={{
            color: "#475569",
            fontSize: "0.82rem",
            fontFamily: "'IBM Plex Mono', monospace",
          }}
        >
          No entities detected.
        </p>
      )}
    </div>
  );
}