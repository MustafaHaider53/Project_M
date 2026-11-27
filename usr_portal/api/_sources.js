/**
 * Shared Supabase multi-source loader and paginated REST helper.
 *
 * Supports two easy ways to configure schools in Vercel Environment Variables
 * (and you can even mix both — duplicates by `id` are deduplicated):
 *
 * 1) Individual per-school env vars (recommended — short values, no JSON escaping):
 *      MAIN_SUPABASE_URL / MAIN_SUPABASE_KEY
 *      INTER_SCHOOL_SUPABASE_URL / INTER_SCHOOL_SUPABASE_KEY
 *      AFTER_SCHOOL_SUPABASE_URL / AFTER_SCHOOL_SUPABASE_KEY
 *      SIBYAAN_SUPABASE_URL / SIBYAAN_SUPABASE_KEY
 *    Or generic numbered vars for any additional school (N = 1..20):
 *      SUPABASE_SOURCE_1_URL / SUPABASE_SOURCE_1_KEY (+ optional _ID, _LABEL, _COLOR)
 *
 * 2) Combined JSON array:
 *      SUPABASE_SOURCES_JSON='[{"id":"main","label":"Main / Mukhayyam","color":"#0E6B50","url":"https://...","key":"..."}]'
 */

const NAMED_SCHOOLS = [
  { prefix: "MAIN", id: "main", label: "Main / Mukhayyam", color: "#0E6B50" },
  { prefix: "INTER_SCHOOL", id: "inter_school", label: "Inter-School", color: "#1d4ed8" },
  { prefix: "AFTER_SCHOOL", id: "after_school", label: "After-School", color: "#7e22ce" },
  { prefix: "SIBYAAN", id: "sibyaan", label: "Sibyaan", color: "#d97706" },
];

function normalizeSource(s, idx) {
  return {
    id: String(s.id || `source_${idx + 1}`).trim(),
    label: String(s.label || s.id || `School ${idx + 1}`).trim(),
    color: String(s.color || "#0E6B50").trim(),
    url: String(s.url || "").trim().replace(/\/+$/, ""),
    key: String(s.key || "").trim(),
    schema: s.schema ? String(s.schema).trim() : "",
  };
}

export function getSources() {
  const sources = [];
  const seenIds = new Set();

  const addSource = (s) => {
    const norm = normalizeSource(s, sources.length);
    if (!norm.url || !norm.key) return;
    if (seenIds.has(norm.id)) return;
    seenIds.add(norm.id);
    sources.push(norm);
  };

  // Merge process.env with optional KEY=VALUE lines if pasted inside SUPABASE_SOURCES_JSON
  const envMap = { ...process.env };

  // 1) Optional JSON array OR KEY=VALUE lines in SUPABASE_SOURCES_JSON
  const raw = (process.env.SUPABASE_SOURCES_JSON || "").trim();
  if (raw) {
    if (raw.startsWith("[")) {
      let parsed;
      try {
        parsed = JSON.parse(raw);
      } catch (err) {
        throw new Error(
          `Invalid JSON in SUPABASE_SOURCES_JSON: ${err.message} (length=${raw.length}, endsWith=${JSON.stringify(raw.slice(-15))})`
        );
      }
      if (!Array.isArray(parsed)) {
        throw new Error("SUPABASE_SOURCES_JSON must be a JSON array.");
      }
      for (const item of parsed) addSource(item);
    } else if (raw.includes("=")) {
      for (const line of raw.split(/\r?\n/)) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#")) continue;
        const eq = trimmed.indexOf("=");
        if (eq <= 0) continue;
        const k = trimmed.slice(0, eq).trim();
        const v = trimmed.slice(eq + 1).trim().replace(/^["']|["']$/g, "");
        if (k && v) envMap[k] = v;
      }
    } else {
      throw new Error(
        `Invalid format in SUPABASE_SOURCES_JSON (length=${raw.length}, endsWith=${JSON.stringify(raw.slice(-15))})`
      );
    }
  }

  // 2) Named per-school env vars (MAIN_*, INTER_SCHOOL_*, AFTER_SCHOOL_*, SIBYAAN_*)
  for (const cfg of NAMED_SCHOOLS) {
    const url = (envMap[`${cfg.prefix}_SUPABASE_URL`] || "").trim();
    const key = (envMap[`${cfg.prefix}_SUPABASE_KEY`] || "").trim();
    if (url && key) {
      addSource({
        id: cfg.id,
        label: (envMap[`${cfg.prefix}_LABEL`] || cfg.label).trim(),
        color: (envMap[`${cfg.prefix}_COLOR`] || cfg.color).trim(),
        url,
        key,
      });
    }
  }

  // 3) Generic numbered per-school env vars (SUPABASE_SOURCE_1_URL / _KEY .. 20)
  for (let i = 1; i <= 20; i++) {
    const url = (envMap[`SUPABASE_SOURCE_${i}_URL`] || "").trim();
    const key = (envMap[`SUPABASE_SOURCE_${i}_KEY`] || "").trim();
    if (url && key) {
      addSource({
        id: (envMap[`SUPABASE_SOURCE_${i}_ID`] || `source_${i}`).trim(),
        label: (envMap[`SUPABASE_SOURCE_${i}_LABEL`] || `School ${i}`).trim(),
        color: (envMap[`SUPABASE_SOURCE_${i}_COLOR`] || "#0E6B50").trim(),
        url,
        key,
      });
    }
  }

  if (sources.length === 0) {
    throw new Error(
      "No Supabase sources configured. Set SUPABASE_SOURCES_JSON or individual *_SUPABASE_URL / *_SUPABASE_KEY variables in Vercel Project Settings -> Environment Variables."
    );
  }
  return sources;
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
