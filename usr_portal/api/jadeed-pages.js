import { getSources, supabaseSelectAll, nowPKT } from "./_sources.js";

const IGNORED_NAMES = new Set(["test_student"]);
const MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_LONG = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function pad2(n) {
  return String(n).padStart(2, "0");
}

function daysInMonth(year, month) {
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function shiftMonth(year, month, delta) {
  const total = year * 12 + (month - 1) + delta;
  const ny = Math.floor(total / 12);
  const nm = ((total % 12) + 12) % 12 + 1;
  return { year: ny, month: nm };
}

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

  const rawMonths = parseInt(req.query?.months, 10);
  const numMonths = Number.isFinite(rawMonths) ? Math.max(1, Math.min(12, rawMonths)) : 3;

  const today = nowPKT();
  const months = [];
  // Build chronologically oldest -> newest (e.g. Sep, Oct, Nov)
  for (let delta = -(numMonths - 1); delta <= 0; delta++) {
    const { year, month } = shiftMonth(today.year, today.month, delta);
    months.push({
      key: `${year}-${pad2(month)}`,
      year,
      month,
      short: MONTH_SHORT[month - 1],
      short_yr: `${MONTH_SHORT[month - 1]} '${String(year).slice(2)}`,
      full: `${MONTH_LONG[month - 1]} ${year}`,
    });
  }

  const oldest = months[0];
  const newest = months[months.length - 1];
  const fromDate = `${oldest.year}-${pad2(oldest.month)}-01`;
  const toDate = `${newest.year}-${pad2(newest.month)}-${pad2(daysInMonth(newest.year, newest.month))}`;
  const dateFilter = `(activity_date.gte.${fromDate},activity_date.lte.${toDate})`;

  const settled = await Promise.allSettled(
    sources.map(async (src) => {
      const [students, jadeedRows] = await Promise.all([
        supabaseSelectAll(src, "students", {
          select: "id,full_name,its",
          order: "full_name.asc",
        }).catch(() =>
          supabaseSelectAll(src, "students", {
            select: "id,full_name",
            order: "full_name.asc",
          })
        ),
        supabaseSelectAll(
          src,
          "jadeed_entries",
          {
            select: "student_id,activity_date,surah_id,page_number,ayah_number,surahs(number,name_en)",
            and: dateFilter,
            order: "activity_date.asc,created_at.asc",
          },
          20000,
          15000
        ),
      ]);
      return { src, students, jadeedRows };
    })
  );

  const sourceSummaries = [];
  const rows = [];
  const warnings = [];
  const currMonthKey = newest.key;

  settled.forEach((outcome, idx) => {
    const src = sources[idx];
    if (outcome.status !== "fulfilled") {
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
      return;
    }

    const { students, jadeedRows } = outcome.value;

    // Group jadeed entries by student_id
    const byStudent = new Map();
    for (const j of jadeedRows) {
      const sid = j.student_id;
      if (!sid) continue;
      if (!byStudent.has(sid)) byStudent.set(sid, []);
      byStudent.get(sid).push(j);
    }

    let validCount = 0;
    for (const st of students) {
      const name = String(st.full_name || "").trim();
      if (!name || IGNORED_NAMES.has(name.toLowerCase()) || name.toLowerCase().includes("test_student")) {
        continue;
      }
      validCount++;
      const rawIts = st.its != null ? String(st.its).split(".")[0].trim() : "";
      const entries = byStudent.get(st.id) || [];

      // Exact Project_M formula: per month, per Surah -> max(page) - min(page) + 1
      const monthSurahPages = {};
      for (const m of months) monthSurahPages[m.key] = new Map();

      for (const e of entries) {
        const actDate = String(e.activity_date || "");
        const mKey = actDate.slice(0, 7);
        if (!monthSurahPages[mKey]) continue;

        let sInfo = e.surahs;
        if (Array.isArray(sInfo)) sInfo = sInfo[0] || {};
        sInfo = sInfo || {};
        const sNum = Number(sInfo.number || e.surah_id || 0);
        const pNum = parseInt(e.page_number, 10);

        if (sNum > 0 && Number.isFinite(pNum) && pNum > 0) {
          const sMap = monthSurahPages[mKey];
          if (!sMap.has(sNum)) {
            sMap.set(sNum, { min: pNum, max: pNum });
          } else {
            const cur = sMap.get(sNum);
            if (pNum < cur.min) cur.min = pNum;
            if (pNum > cur.max) cur.max = pNum;
          }
        }
      }

      const monthPages = {};
      let totalPages = 0;
      for (const m of months) {
        let mTot = 0;
        for (const span of monthSurahPages[m.key].values()) {
          mTot += span.max - span.min + 1;
        }
        monthPages[m.key] = mTot;
        totalPages += mTot;
      }

      let latest = null;
      if (entries.length > 0) {
        const last = entries[entries.length - 1];
        let sInfo = last.surahs;
        if (Array.isArray(sInfo)) sInfo = sInfo[0] || {};
        sInfo = sInfo || {};
        latest = {
          surah: sInfo.name_en || "",
          page: last.page_number != null ? String(last.page_number) : "",
          ayah: last.ayah_number != null ? String(last.ayah_number) : "",
          date: String(last.activity_date || ""),
        };
      }

      rows.push({
        id: st.id,
        name,
        its: rawIts,
        source_id: src.id,
        source_label: src.label,
        source_color: src.color,
        months: monthPages,
        total: totalPages,
        current_month: monthPages[currMonthKey] || 0,
        entries_count: entries.length,
        latest,
      });
    }

    sourceSummaries.push({
      id: src.id,
      label: src.label,
      color: src.color,
      count: validCount,
      ok: true,
    });
  });

  // Default sort: highest total pages first, then current month desc, then A-Z
  rows.sort((a, b) => {
    if (b.total !== a.total) return b.total - a.total;
    if (b.current_month !== a.current_month) return b.current_month - a.current_month;
    return a.name.localeCompare(b.name, undefined, { sensitivity: "base" });
  });

  if (req.query?.refresh === "1") {
    res.setHeader("Cache-Control", "no-store");
  } else {
    res.setHeader("Cache-Control", "public, s-maxage=120, stale-while-revalidate=600");
  }

  return res.status(200).json({
    today_iso: today.iso,
    months,
    sources: sourceSummaries,
    rows,
    warnings,
    fetched_at: new Date().toISOString(),
  });
}
