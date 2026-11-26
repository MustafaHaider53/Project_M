import { getSources, supabaseSelectAll } from "./_sources.js";

const IGNORED_NAMES = new Set(["test_student"]);

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Content-Type", "application/json; charset=utf-8");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  let sources;
  try {
    sources = getSources();
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }

  // Fetch all configured Supabase student lists in parallel
  const settled = await Promise.allSettled(
    sources.map(async (src) => {
      let rows;
      try {
        rows = await supabaseSelectAll(src, "students", {
          select: "id,full_name,its",
          order: "full_name.asc",
        });
      } catch {
        // Fallback if a legacy Supabase instance doesn't have an `its` column yet
        rows = await supabaseSelectAll(src, "students", {
          select: "id,full_name",
          order: "full_name.asc",
        });
      }
      return { src, rows };
    })
  );

  const sourceSummaries = [];
  const students = [];
  const warnings = [];

  settled.forEach((outcome, idx) => {
    const src = sources[idx];
    if (outcome.status === "fulfilled") {
      const { rows } = outcome.value;
      let validCount = 0;
      for (const r of rows) {
        const name = String(r.full_name || "").trim();
        if (!name || IGNORED_NAMES.has(name.toLowerCase())) continue;
        validCount++;
        const rawIts = r.its != null ? String(r.its).split(".")[0].trim() : "";
        students.push({
          id: r.id,
          name,
          its: rawIts,
          source_id: src.id,
          source_label: src.label,
          source_color: src.color,
        });
      }
      sourceSummaries.push({
        id: src.id,
        label: src.label,
        color: src.color,
        count: validCount,
        ok: true,
      });
    } else {
      const reason = outcome.reason?.message || "Connection failed";
      warnings.push(`${src.label}: ${reason}`);
      sourceSummaries.push({
        id: src.id,
        label: src.label,
        color: src.color,
        count: 0,
        ok: false,
        error: reason,
      });
    }
  });

  // Sort unified list alphabetically by student name
  students.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: "base" }));

  // Cache on Vercel CDN edge for 2 minutes (stale-while-revalidate 10 min) unless ?refresh=1
  if (req.query?.refresh === "1") {
    res.setHeader("Cache-Control", "no-store");
  } else {
    res.setHeader("Cache-Control", "public, s-maxage=120, stale-while-revalidate=600");
  }

  return res.status(200).json({
    sources: sourceSummaries,
    students,
    warnings,
    fetched_at: new Date().toISOString(),
  });
}
