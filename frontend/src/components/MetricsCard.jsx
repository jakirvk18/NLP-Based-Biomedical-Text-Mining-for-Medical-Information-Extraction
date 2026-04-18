import React from "react";

/* Progress bar */
function Progress({ value, color }) {
  return (
    <div
      style={{
        height: 4,
        background: "#1e293b",
        borderRadius: 999,
        marginTop: "0.5rem",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${(value * 100).toFixed(1)}%`,
          background: color,
          borderRadius: 999,
          transition: "width 0.8s ease",
        }}
      />
    </div>
  );
}

/* Metric box */
function Metric({ title, value, color }) {
  const percent = ((value || 0) * 100).toFixed(1);

  return (
    <div
      style={{
        flex: 1,
        padding: "1rem",
        textAlign: "center",
        borderRadius: 10,
        background: "#0a0e1a",
      }}
    >
      <div
        style={{
          fontSize: "1.7rem",
          fontWeight: 700,
          color,
          fontFamily: "'IBM Plex Mono', monospace",
        }}
      >
        {percent}%
      </div>

      <div
        style={{
          fontSize: "0.65rem",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "#64748b",
          marginTop: "0.3rem",
          fontFamily: "'IBM Plex Mono', monospace",
        }}
      >
        {title}
      </div>

      <Progress value={value || 0} color={color} />
    </div>
  );
}

/* Small badge */
function Badge({ text }) {
  return (
    <span
      style={{
        background: "#2a1a00",
        border: "1px solid #f59e0b",
        borderRadius: 999,
        fontSize: "0.65rem",
        color: "#fbbf24",
        padding: "0.15rem 0.55rem",
        fontFamily: "'IBM Plex Mono', monospace",
      }}
    >
      {text}
    </span>
  );
}

export default function MetricsCard({ metrics = {}, summary }) {
  const {
    precision = 0,
    recall = 0,
    f1 = 0,
    entities_found = 0,
    relations_found = 0,
    entity_breakdown = {},
    mode,
  } = metrics;

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
            background: "#0a2a1a",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          📊
        </div>

        <span
          style={{
            fontSize: "0.82rem",
            fontWeight: 700,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            fontFamily: "'IBM Plex Mono', monospace",
            color: "#34d399",
          }}
        >
          Evaluation Metrics
        </span>

        {mode === "estimated" && (
          <span style={{ marginLeft: "auto" }}>
            <Badge text="estimated" />
          </span>
        )}
      </div>

      {/* Metrics */}
      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <Metric title="Precision" value={precision} color="#38bdf8" />
        <Metric title="Recall" value={recall} color="#a78bfa" />
        <Metric title="F1 Score" value={f1} color="#34d399" />
      </div>

      {/* Counts */}
      <div
        style={{
          marginTop: "0.85rem",
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
          fontSize: "0.75rem",
          color: "#64748b",
          fontFamily: "'IBM Plex Mono', monospace",
        }}
      >
        <span>{entities_found} entities</span>
        <span style={{ color: "#334155" }}>·</span>
        <span>{relations_found} relations</span>
      </div>

      {/* Breakdown */}
      {Object.keys(entity_breakdown).length > 0 && (
        <div style={{ marginTop: "0.85rem" }}>
          <div
            style={{
              fontSize: "0.65rem",
              color: "#475569",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              marginBottom: "0.5rem",
              fontFamily: "'IBM Plex Mono', monospace",
            }}
          >
            Breakdown
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
            {Object.entries(entity_breakdown).map(([key, value]) => (
              <span
                key={key}
                style={{
                  background: "#1e293b",
                  borderRadius: 6,
                  padding: "0.2rem 0.5rem",
                  fontSize: "0.72rem",
                  color: "#94a3b8",
                  fontFamily: "'IBM Plex Mono', monospace",
                }}
              >
                {key}: {value}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div
          style={{
            marginTop: "0.85rem",
            padding: "0.75rem",
            background: "#0a0e1a",
            borderRadius: 8,
            border: "1px solid #1e293b",
            fontSize: "0.78rem",
            color: "#94a3b8",
            lineHeight: 1.6,
            fontFamily: "'IBM Plex Mono', monospace",
          }}
        >
          {summary}
        </div>
      )}
    </div>
  );
}