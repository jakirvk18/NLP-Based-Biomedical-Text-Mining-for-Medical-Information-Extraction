// api.js
// Centralized API layer for Flask NLP backend

const API_BASE = "http://localhost:5000"; // or use env vars
async function request(url, options = {}, timeout = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(id);

    let data = null;
    try {
      data = await response.json();
    } catch (_) {
      /* ignore json parse errors */
    }

    if (!response.ok) {
      const message =
        data?.error ||
        data?.message ||
        `Request failed with status ${response.status}`;
      throw new Error(message);
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timeout. Backend took too long.");
    }
    throw error;
  }
}

/**
 * Send biomedical text to backend NLP pipeline
 *
 * @param {string} text
 * @returns {Promise<{entities, relations, highlighted_text, metrics, summary}>}
 */
export async function analyzeText(text) {
  if (!text || !text.trim()) {
    throw new Error("Input text cannot be empty");
  }

  return request("/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });
}