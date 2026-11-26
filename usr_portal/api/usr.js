import { getSourceById, supabaseSelect, nowPKT } from "./_sources.js";

const SIPARA_TO_SURAH = {
  1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8,
  11: 9, 12: 11, 13: 12, 14: 15, 15: 17, 16: 18, 17: 21, 18: 23, 19: 25, 20: 27,
  21: 29, 22: 33, 23: 36, 24: 39, 25: 41, 26: 46, 27: 51, 28: 58, 29: 67, 30: 78,
};

const SIPARA_NAMES = {
  1: "Sipara 1", 2: "Sipara 2", 3: "Sipara 3", 4: "Sipara 4", 5: "Sipara 5",
  6: "Sipara 6", 7: "Sipara 7", 8: "Sipara 8", 9: "Sipara 9", 10: "Sipara 10",
  11: "Sipara 11", 12: "Sipara 12", 13: "Sipara 13", 14: "Sipara 14", 15: "Sipara 15",
  16: "Sipara 16", 17: "Sipara 17", 18: "Sipara 18", 19: "Sipara 19", 20: "Sipara 20",
  21: "Sipara 21", 22: "Sipara 22", 23: "Sipara 23", 24: "Sipara 24", 25: "Sipara 25",
  26: "Sipara 26", 27: "Sipara 27", 28: "Sipara 28", 29: "Sipara 29", 30: "Sipara 30",
};

const MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_LONG = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const DAY_SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function daysInMonth(year, month) {
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function monthKey(year, month) {
  return `${year}-${String(month).padStart(2, "0")}`;
}

function shiftMonth(year, month, delta) {
  const total = year * 12 + (month - 1) + delta;
  const ny = Math.floor(total / 12);
  const nm = ((total % 12) + 12) % 12 + 1;
  return { year: ny, month: nm };
}

function pad2(n) {
  return String(n).padStart(2, "0");
}

function buildMonthPayload(year, month, grouped, todayIso) {
  const lastDay = daysInMonth(year, month);
  const days = [];

  let totalWorkingDays = 0;
  let totalActiveDays = 0;
  let murajatPages = 0;
  let murajatMarksSum = 0;
  let murajatMarksCount = 0;
  let juzulhaliPages = 0;
  let juzulhaliMarksSum = 0;
  let juzulhaliMarksCount = 0;
  let jadeedCount = 0;

  for (let d = 1; d <= lastDay; d++) {
    const iso = `${year}-${pad2(month)}-${pad2(d)}`;
    const jsWd = new Date(Date.UTC(year, month - 1, d)).getUTCDay(); // 0=Sun, 6=Sat
    const isWeekend = jsWd === 0 || jsWd === 6;
    const dayName = DAY_SHORT[jsWd];

    const rec = grouped[iso] || {
      murajat: [],
      juzulhali: [],
      jadeed: [],
      no_jadeed: false,
      no_jadeed_reasons: [],
      has_hw: false,
    };

    if (!isWeekend && iso <= todayIso) {
      totalWorkingDays++;
    }

    const hasActivity = Boolean(
      rec.murajat.length || rec.juzulhali.length || rec.jadeed.length || rec.no_jadeed || rec.has_hw
    );
    if (hasActivity && !isWeekend) {
      totalActiveDays++;
    }

    for (const m of rec.murajat) {
      murajatPages += 1;
      if (typeof m.marks === "number") {
        murajatMarksSum += m.marks;
        murajatMarksCount++;
      }
    }

    for (const j of rec.juzulhali) {
      const pVal = Number(j.page);
      juzulhaliPages += pVal >= 1 && pVal <= 30 ? pVal : 1;
      if (typeof j.marks === "number") {
        juzulhaliMarksSum += j.marks;
        juzulhaliMarksCount++;
      }
    }

    jadeedCount += rec.jadeed.length;

    const isAbsent =
      !isWeekend &&
      iso <= todayIso &&
      !rec.murajat.length &&
      !rec.juzulhali.length &&
      !rec.jadeed.length &&
      !rec.no_jadeed &&
      !rec.has_hw;

    const isWeekendEmpty =
      isWeekend &&
      !rec.murajat.length &&
      !rec.juzulhali.length &&
      !rec.jadeed.length &&
      !rec.no_jadeed &&
      !rec.has_hw;

    days.push({
      day: d,
      date: iso,
      ddmm: `${pad2(d)}/${pad2(month)}`,
      dow: dayName,
      is_weekend: isWeekend,
      is_sunday: jsWd === 0,
      is_future: iso > todayIso,
      is_absent: isAbsent,
      is_weekend_empty: isWeekendEmpty,
      murajat: rec.murajat,
      juzulhali: rec.juzulhali,
      jadeed: rec.jadeed,
      no_jadeed: rec.no_jadeed,
      no_jadeed_reasons: rec.no_jadeed_reasons,
    });
  }

  const attendancePct =
    totalWorkingDays > 0 ? Math.round((totalActiveDays / totalWorkingDays) * 1000) / 10 : 100.0;
  const avgMurajat =
    murajatMarksCount > 0 ? Math.round((murajatMarksSum / murajatMarksCount) * 10) / 10 : null;
  const avgJuzulhali =
    juzulhaliMarksCount > 0 ? Math.round((juzulhaliMarksSum / juzulhaliMarksCount) * 10) / 10 : null;

  return {
    key: monthKey(year, month),
    year,
    month,
    short_label: `${MONTH_SHORT[month - 1]} ${String(year).slice(2)}`,
    full_label: `${MONTH_LONG[month - 1]} ${year}`,
    stats: {
      active_days: totalActiveDays,
      working_days: totalWorkingDays,
      attendance_pct: attendancePct,
      murajat_count: murajatPages,
      murajat_avg: avgMurajat,
      juzulhali_pages: juzulhaliPages,
      juzulhali_avg: avgJuzulhali,
      jadeed_count: jadeedCount,
    },
    days,
  };
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Content-Type", "application/json; charset=utf-8");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  const sourceId = String(req.query?.source || "").trim();
  const studentId = String(req.query?.student_id || "").trim();
  if (!sourceId || !studentId) {
    return res.status(400).json({ error: "Missing required query parameters: source and student_id" });
  }

  let source;
  try {
    source = getSourceById(sourceId);
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
  if (!source) {
    return res.status(404).json({ error: `Unknown source '${sourceId}'` });
  }

  const today = nowPKT();

  // Determine month window:
  // - If ?year=&month= provided -> fetch that exact 1 month on demand
  // - Otherwise -> prefetch last 3 months (current, -1, -2) in ONE parallel DB round-trip!
  let targetMonths = [];
  const qYear = parseInt(req.query?.year, 10);
  const qMonth = parseInt(req.query?.month, 10);

  if (qYear >= 2020 && qYear <= 2035 && qMonth >= 1 && qMonth <= 12) {
    targetMonths = [{ year: qYear, month: qMonth }];
  } else {
    targetMonths = [
      { year: today.year, month: today.month },
      shiftMonth(today.year, today.month, -1),
      shiftMonth(today.year, today.month, -2),
    ];
  }

  const oldest = targetMonths[targetMonths.length - 1];
  const newest = targetMonths[0];
  const fromDate = `${oldest.year}-${pad2(oldest.month)}-01`;
  const toDate = `${newest.year}-${pad2(newest.month)}-${pad2(daysInMonth(newest.year, newest.month))}`;
  const dateFilter = `(activity_date.gte.${fromDate},activity_date.lte.${toDate})`;

  try {
    // 4 concurrent slim queries against the student's Supabase project
    const [sessionRows, jadeedRows, dailyRows, takhteetRows] = await Promise.all([
      supabaseSelect(source, "listening_sessions", {
        select:
          "id,activity_date,mode,surah_id,page_number,duration_seconds,created_at,surahs(number,name_en,name_ar),mistake_counts(talqeen,tanbeeh,is_zero_marks,manual_marks)",
        student_id: `eq.${studentId}`,
        and: dateFilter,
        order: "activity_date.asc,created_at.asc",
      }).catch(() =>
        supabaseSelect(source, "listening_sessions", {
          select:
            "id,activity_date,mode,surah_id,page_number,created_at,surahs(number,name_en,name_ar),mistake_counts(talqeen,tanbeeh,is_zero_marks,manual_marks)",
          student_id: `eq.${studentId}`,
          and: dateFilter,
          order: "activity_date.asc,created_at.asc",
        })
      ),
      supabaseSelect(source, "jadeed_entries", {
        select:
          "id,activity_date,surah_id,page_number,ayah_number,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,weak_murajat,weak_juzulhali,created_at,surahs(number,name_en,name_ar)",
        student_id: `eq.${studentId}`,
        and: dateFilter,
        order: "activity_date.asc,created_at.asc",
      }).catch(() =>
        supabaseSelect(source, "jadeed_entries", {
          select: "id,activity_date,surah_id,page_number,ayah_number,created_at,surahs(number,name_en,name_ar)",
          student_id: `eq.${studentId}`,
          and: dateFilter,
          order: "activity_date.asc,created_at.asc",
        })
      ),
      supabaseSelect(source, "jadeed_daily", {
        select: "activity_date,no_jadeed,weak_hifz,airab_mistakes,time_exceeded,weak_murajat,weak_juzulhali",
        student_id: `eq.${studentId}`,
        and: dateFilter,
        order: "activity_date.asc",
      }).catch(() =>
        supabaseSelect(source, "jadeed_daily", {
          select: "activity_date,no_jadeed",
          student_id: `eq.${studentId}`,
          and: dateFilter,
          order: "activity_date.asc",
        })
      ),
      supabaseSelect(source, "takhteet_daily", {
        select: "activity_date,murajat_text_raw,juzulhali_text_raw,jadeed_text_raw",
        student_id: `eq.${studentId}`,
        and: dateFilter,
        order: "activity_date.asc",
      }).catch(() => []),
    ]);

    const grouped = {};
    const ensure = (d) => {
      if (!grouped[d]) {
        grouped[d] = {
          murajat: [],
          juzulhali: [],
          jadeed: [],
          no_jadeed: false,
          no_jadeed_reasons: [],
          has_hw: false,
        };
      }
      return grouped[d];
    };

    // Process Murajat & Juzulhali listening sessions
    for (const s of sessionRows) {
      const d = String(s.activity_date || "");
      if (!d) continue;
      let mc = s.mistake_counts;
      if (Array.isArray(mc)) mc = mc[0] || null;
      if (!mc) continue;

      const talqeen = Number(mc.talqeen || 0);
      const tanbeeh = Number(mc.tanbeeh || 0);
      const isZero = Boolean(mc.is_zero_marks);
      let marks;
      if (mc.manual_marks !== null && mc.manual_marks !== undefined) {
        marks = Number(mc.manual_marks);
      } else if (isZero) {
        marks = 0;
      } else {
        marks = Math.max(0, 10 - 0.5 * talqeen - 0.25 * tanbeeh);
      }
      marks = Math.round(marks * 10) / 10;

      let surah = s.surahs;
      if (Array.isArray(surah)) surah = surah[0] || {};
      surah = surah || {};

      const pNum = Number(s.page_number || 0);
      const surahId = s.surah_id != null ? Number(s.surah_id) : null;
      let label = surah.name_en || surah.name_ar || "";
      let pageOut = s.page_number != null ? String(s.page_number) : "-";

      const dur = Number(s.duration_seconds || 0);
      const target = ensure(d);

      if (s.mode === "murajat") {
        if (pNum >= 1 && pNum <= 30 && (surahId === SIPARA_TO_SURAH[pNum] || !label || label === "Surah")) {
          label = SIPARA_NAMES[pNum] || `Sipara ${pNum}`;
          pageOut = "-";
        }
        target.murajat.push({
          surah: label || "-",
          page: pageOut,
          marks,
          dur,
          over: dur > 600,
        });
      } else if (s.mode === "juzulhali") {
        if (surahId && pNum >= 1 && pNum <= 30 && surahId === SIPARA_TO_SURAH[pNum]) {
          label = SIPARA_NAMES[pNum] || `Sipara ${pNum}`;
          pageOut = "-";
        } else if (!label) {
          label = "Juz'Hali";
        }
        target.juzulhali.push({
          surah: label,
          page: pageOut,
          marks,
          dur,
          over: dur > 900,
        });
      }
    }

    // Process Jadeed entries
    for (const j of jadeedRows) {
      const d = String(j.activity_date || "");
      if (!d) continue;
      let surah = j.surahs;
      if (Array.isArray(surah)) surah = surah[0] || {};
      surah = surah || {};
      const flags = [];
      if (j.weak_hifz) flags.push("Weak Hifz");
      if (j.airab_mistakes) flags.push("Airab");
      if (j.weak_murajat) flags.push("Weak Mur");
      if (j.weak_juzulhali) flags.push("Weak JH");
      const dur = Number(j.duration_seconds || 0);
      ensure(d).jadeed.push({
        surah: surah.name_en || surah.name_ar || "-",
        page: j.page_number != null ? String(j.page_number) : "-",
        ayah: j.ayah_number != null ? String(j.ayah_number) : "-",
        dur,
        over: Boolean(j.time_exceeded || dur > 300),
        flags,
      });
    }

    // Process No-Jadeed daily statuses
    for (const dj of dailyRows) {
      const d = String(dj.activity_date || "");
      if (!d) continue;
      const target = ensure(d);
      if (dj.no_jadeed) {
        target.no_jadeed = true;
        const reasons = [];
        if (dj.weak_hifz) reasons.push("Weak Hifz");
        if (dj.airab_mistakes) reasons.push("Airab");
        if (dj.time_exceeded) reasons.push("Time Exceeded");
        if (dj.weak_murajat) reasons.push("Weak Murajat");
        if (dj.weak_juzulhali) reasons.push("Weak JH");
        target.no_jadeed_reasons = reasons;
      }
    }

    // Process Homework (Takhteet) existence for attendance parity
    for (const tk of takhteetRows) {
      const d = String(tk.activity_date || "");
      if (!d) continue;
      if (
        (tk.murajat_text_raw && tk.murajat_text_raw.trim()) ||
        (tk.juzulhali_text_raw && tk.juzulhali_text_raw.trim()) ||
        (tk.jadeed_text_raw && tk.jadeed_text_raw.trim())
      ) {
        ensure(d).has_hw = true;
      }
    }

    // Slice into per-month USR objects
    const months = {};
    for (const tm of targetMonths) {
      const payload = buildMonthPayload(tm.year, tm.month, grouped, today.iso);
      months[payload.key] = payload;
    }

    res.setHeader("Cache-Control", "public, s-maxage=30, stale-while-revalidate=120");
    return res.status(200).json({
      source_id: source.id,
      source_label: source.label,
      student_id: studentId,
      today_iso: today.iso,
      months,
    });
  } catch (err) {
    return res.status(500).json({ error: err.message || "Failed to fetch USR data" });
  }
}
