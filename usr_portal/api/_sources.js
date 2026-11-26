/**
 * Shared Supabase multi-source loader and paginated REST helper.
 *
 * Configure unlimited Supabase projects via the Vercel Environment Variable:
 *   SUPABASE_SOURCES_JSON='[
 *     {"id":"main","label":"Main / Mukhayyam","color":"#0E6B50","url":"https://...","key":"..."},
 *     {"id":"inter_school","label":"Inter-School","color":"#1d4ed8","url":"https://...","key":"..."},
 *     {"id":"after_school","label":"After-School","color":"#7e22ce","url":"https://...","key":"..."}
 *   ]'
 */

export function getSources() {
  const raw = (process.env.SUPABASE_SOURCES_JSON || "").trim();
  if (!raw) {
    throw new Error(
      "SUPABASE_SOURCES_JSON environment variable is not set. Add your Supabase projects JSON in Vercel Project Settings -> Environment Variables."
    );
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new Error(`Invalid JSON in SUPABASE_SOURCES_JSON: ${err.message}`);
  }
  if (!Array.isArray(parsed) || parsed.length === 0) {
    throw new Error("SUPABASE_SOURCES_JSON must be a non-empty JSON array.");
  }
  return parsed.map((s, idx) => ({
    id: String(s.id || `source_${idx + 1}`).trim(),
    label: String(s.label || s.id || `School ${idx + 1}`).trim(),
    color: String(s.color || "#0E6B50").trim(),
    url: String(s.url || "").replace(/\/+$/, ""),
    key: String(s.key || "").trim(),
    schema: s.schema ? String(s.schema).trim() : "",
  }));
}

export function getSourceById(sourceId) {
  const sources = getSources();
  return sources.find((s) => s.id === sourceId) || null;
}

export function buildHeaders(source, extra = {}) {
  const h = {
    apikey: source.key,
    Authorization: `Bearer ${source.key}`,
    Accept: "application/json",
    ...extra,
  };
  if (source.schema && source.schema !== "public") {
    h["Accept-Profile"] = source.schema;
  }
  return h;
}

/**
 * Single REST query to a Supabase table.
 */
export async function supabaseSelect(source, table, params = {}, timeoutMs = 12000) {
  const qs = new URLSearchParams(params).toString();
  const url = `${source.url}/rest/v1/${table}${qs ? `?${qs}` : ""}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: buildHeaders(source),
      signal: controller.signal,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} on ${table}: ${text.slice(0, 200)}`);
    }
    const text = await res.text();
    return text.trim() ? JSON.parse(text) : [];
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Paginated REST query (chunks of 1000 rows) so large rosters (>1000 students) are never truncated.
 */
export async function supabaseSelectAll(source, table, params = {}, maxRows = 5000, timeoutMs = 12000) {
  const pageSize = 1000;
  const all = [];
  let offset = 0;
  const qs = new URLSearchParams(params).toString();
  const baseUrl = `${source.url}/rest/v1/${table}${qs ? `?${qs}` : ""}`;

  while (offset < maxRows) {
    const end = Math.min(offset + pageSize - 1, maxRows - 1);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(baseUrl, {
        method: "GET",
        headers: buildHeaders(source, {
          "Range-Unit": "items",
          Range: `${offset}-${end}`,
        }),
        signal: controller.signal,
      });
      if (res.status === 416) break; // Reached end cleanly
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status} on ${table}: ${text.slice(0, 200)}`);
      }
      const text = await res.text();
      const batch = text.trim() ? JSON.parse(text) : [];
      all.push(...batch);
      if (batch.length < pageSize) break;
      offset += pageSize;
    } finally {
      clearTimeout(timer);
    }
  }
  return all;
}

/**
 * Current date in Pakistan Standard Time (UTC+5) as { year, month, day, iso }.
 */
export function nowPKT() {
  const pktMs = Date.now() + 5 * 60 * 60 * 1000;
  const d = new Date(pktMs);
  const year = d.getUTCFullYear();
  const month = d.getUTCMonth() + 1;
  const day = d.getUTCDate();
  const iso = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
  return { year, month, day, iso };
}
