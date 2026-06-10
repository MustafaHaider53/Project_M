from __future__ import annotations

from html import escape
from typing import Any, Dict, List
from datetime import datetime, date

AHKAM_LABELS = {
    "ikhfa": "Ikhfa",
    "izhaar": "Izhaar",
    "qalqalah": "Qalqalah",
    "ism_jalalah": "Ism Jalal",
    "tahreek_sakin": "Tahreek",
    "gunnah": "Gunnah",
    "idgham": "Idgham",
    "madd_lazim": "M. Lazim",
    "madd_muttasil": "M. Mutta.",
    "mad_tabaiee": "M. Tabai."
}

MAKHRAJ_CHARS = {
    "makhraj_alif": "أ",
    "makhraj_baa": "ب",
    "makhraj_taa": "ت",
    "makhraj_thaa": "ث",
    "makhraj_jeem": "ج",
    "makhraj_haa": "ح",
    "makhraj_khaa": "خ",
    "makhraj_daal": "د",
    "makhraj_dhaal": "ذ",
    "makhraj_raa": "ر",
    "makhraj_zaa": "ز",
    "makhraj_seen": "س",
    "makhraj_sheen": "ش",
    "makhraj_saad": "ص",
    "makhraj_daad": "ض",
    "makhraj_taa_thick": "ط",
    "makhraj_zaa_thick": "ظ",
    "makhraj_ain": "ع",
    "makhraj_ghain": "غ",
    "makhraj_faa": "ف",
    "makhraj_qaaf": "ق",
    "makhraj_kaaf": "ك",
    "makhraj_laam": "ل",
    "makhraj_meem": "م",
    "makhraj_noon": "ن",
    "makhraj_haa_weak": "هـ",
    "makhraj_waw": "و",
    "makhraj_yaa": "ي"
}


def _get_month_year_str(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return datetime.now().strftime("%B %Y")
    try:
        sorted_rows = sorted(rows, key=lambda x: x.get("activity_date", ""))
        first_dt = datetime.strptime(sorted_rows[0].get("activity_date", ""), "%Y-%m-%d")
        last_dt = datetime.strptime(sorted_rows[-1].get("activity_date", ""), "%Y-%m-%d")
        
        if first_dt.month == last_dt.month:
            return last_dt.strftime("%B %Y")
        else:
            return f"{first_dt.strftime('%b')} - {last_dt.strftime('%b %Y')}"
    except Exception:
        return datetime.now().strftime("%B %Y")


def _format_mistake_badges(m: Dict[str, Any]) -> str:
    badges = []
    # Ahkam
    for col, label in AHKAM_LABELS.items():
        val = m.get(col, 0)
        if val > 0:
            badges.append(
                f'<span class="badge badge-ahkam">{label} ({val})</span>'
            )
    # Makharij
    for col, char in MAKHRAJ_CHARS.items():
        val = m.get(col, 0)
        if val > 0:
            lbl = f"{char}" if val == 1 else f"{char} ({val})"
            badges.append(
                f'<span class="badge badge-makhraj">{lbl}</span>'
            )
    return " ".join(badges) if badges else '<span class="muted">-</span>'


def _format_grade_badge(marks: float) -> str:
    if marks >= 9.0:
        return f'<span class="grade-badge grade-excellent">{marks:.1f}/10</span>'
    elif marks >= 7.5:
        return f'<span class="grade-badge grade-passing">{marks:.1f}/10</span>'
    else:
        return f'<span class="grade-badge grade-warning">{marks:.1f}/10</span>'


def build_report_html(student_name: str, rows: List[Dict[str, Any]], report_type: str = "murajat") -> str:
    report_type = report_type.lower()
    
    # Sort rows chronologically
    sorted_rows = sorted(rows, key=lambda x: x.get("activity_date", ""))
    month_year_str = _get_month_year_str(sorted_rows)

    theme_colors = {
        "murajat": {
            "bg": "linear-gradient(135deg, #0E6B50 0%, #1b4d3e 100%)",
            "border": "#0E6B50",
            "title": "Monthly Murajat Report",
            "arabic_title": "تقرير المراجعة الشهري",
            "colspan": 8
        },
        "juzulhali": {
            "bg": "linear-gradient(135deg, #d35400 0%, #a04000 100%)",
            "border": "#d35400",
            "title": "Monthly Juzulhali Report",
            "arabic_title": "تقرير الجزء الحالي الشهري",
            "colspan": 8
        },
        "jadeed": {
            "bg": "linear-gradient(135deg, #8e44ad 0%, #6c3483 100%)",
            "border": "#8e44ad",
            "title": "Monthly Jadeed Report",
            "arabic_title": "تقرير الجديد الشهري",
            "colspan": 4
        },
        "takhteet": {
            "bg": "linear-gradient(135deg, #2980b9 0%, #1b4f72 100%)",
            "border": "#2980b9",
            "title": "Monthly Takhteet Report",
            "arabic_title": "تقرير التخطيط الشهري",
            "colspan": 3
        }
    }
    
    cfg = theme_colors.get(report_type, theme_colors["murajat"])

    # Calculate statistics dynamically
    total_active_days = 0
    total_items = 0
    grades_sum = 0.0
    grades_count = 0
    
    ahkam_totals = {col: 0 for col in AHKAM_LABELS.keys()}
    makharij_totals = {col: 0 for col in MAKHRAJ_CHARS.keys()}
    
    for r in sorted_rows:
        murajat = r.get("murajat", [])
        juzulhali = r.get("juzulhali", [])
        jadeed = r.get("jadeed", [])
        
        # Determine if day is weekend
        activity_date = r.get("activity_date", "")
        try:
            dt = datetime.strptime(activity_date, "%Y-%m-%d")
            wd = dt.weekday()
        except Exception:
            wd = 0
        is_weekend = wd in (5, 6)
        
        # Check presence
        is_present = bool(murajat or juzulhali or jadeed or not (
            r.get("no_jadeed", True)
            and not (r.get("takhteet") or {}).get("murajat", "").strip()
            and not (r.get("takhteet") or {}).get("juzulhali", "").strip()
            and not (r.get("takhteet") or {}).get("jadeed", "").strip()
        ))
        
        if report_type == "murajat" and murajat:
            total_active_days += 1
            for m in murajat:
                total_items += 1
                for col in AHKAM_LABELS.keys():
                    ahkam_totals[col] += m.get(col, 0)
                for col in MAKHRAJ_CHARS.keys():
                    makharij_totals[col] += m.get(col, 0)
                grades_sum += m.get("marks", 10.0)
                grades_count += 1
                
        elif report_type == "juzulhali" and juzulhali:
            total_active_days += 1
            for j in juzulhali:
                total_items += 1
                for col in AHKAM_LABELS.keys():
                    ahkam_totals[col] += j.get(col, 0)
                for col in MAKHRAJ_CHARS.keys():
                    makharij_totals[col] += j.get(col, 0)
                grades_sum += j.get("marks", 10.0)
                grades_count += 1
                
        elif report_type == "jadeed":
            if jadeed:
                total_active_days += 1
                total_items += len(jadeed)
            elif not r.get("no_jadeed") and is_present:
                # Active day but jadeed entry list empty (e.g. absent/empty day excluded)
                pass
                
        elif report_type == "takhteet":
            t = r.get("takhteet") or {}
            if t.get("murajat", "").strip() or t.get("juzulhali", "").strip() or t.get("jadeed", "").strip():
                total_active_days += 1

    # Render Stats Cards HTML
    stats_html = ""
    if report_type in ("murajat", "juzulhali"):
        avg_grade = (grades_sum / grades_count) if grades_count > 0 else 10.0
        
        # Sort and fetch Top 5 Ahkam mistakes
        sorted_ahkam = sorted(
            [(label, count) for col, label in AHKAM_LABELS.items() if (count := ahkam_totals.get(col, 0)) > 0],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        ahkam_display = ", ".join([lbl for lbl, cnt in sorted_ahkam]) if sorted_ahkam else "None"
        
        # Sort and fetch Top 5 Makharij mistakes
        sorted_makharij = sorted(
            [(char, count) for col, char in MAKHRAJ_CHARS.items() if (count := makharij_totals.get(col, 0)) > 0],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        makharij_display = ", ".join([char for char, cnt in sorted_makharij]) if sorted_makharij else "None"

        stats_html = f"""
        <div class="stats-container">
            <div class="stat-card">
                <span class="stat-title">Days Recited</span>
                <span class="stat-value">{total_active_days} Days</span>
            </div>
            <div class="stat-card">
                <span class="stat-title">Top 5 Ahkam Mistakes</span>
                <span class="stat-value" style="font-size: 9.5pt; font-weight: 600; color: #9b2c2c; line-height: 1.25; margin-top: 2px;">{ahkam_display}</span>
            </div>
            <div class="stat-card">
                <span class="stat-title">Average Score</span>
                <span class="stat-value">{avg_grade:.2f} / 10</span>
            </div>
            <div class="stat-card">
                <span class="stat-title">Top 5 Makharij Mistakes</span>
                <span class="stat-value" style="font-size: 11pt; font-weight: 700; color: #2b6cb0; font-family: 'Amiri', serif; line-height: 1.2; margin-top: 2px;">{makharij_display}</span>
            </div>
        </div>
        """
    elif report_type == "jadeed":
        stats_html = f"""
        <div class="stats-container">
            <div class="stat-card">
                <span class="stat-title">Days Recited</span>
                <span class="stat-value">{total_active_days} Days</span>
            </div>
        </div>
        """
    else: # takhteet
        stats_html = f"""
        <div class="stats-container">
            <div class="stat-card">
                <span class="stat-title">Homework Days Assigned</span>
                <span class="stat-value">{total_active_days} Days</span>
            </div>
        </div>
        """

    table_rows = []
    for idx, r in enumerate(sorted_rows):
        activity_date = r.get("activity_date", "")
        date_num = idx + 1
        
        date_sub = ""
        if len(activity_date) == 10:
            date_sub = f"{activity_date[8:10]}/{activity_date[5:7]}"
            
        try:
            dt = datetime.strptime(activity_date, "%Y-%m-%d")
            wd = dt.weekday()
        except Exception:
            wd = 0
            
        day_names_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_name_en = day_names_en[wd]
        is_weekend = wd in (5, 6)
            
        murajat = r.get("murajat", [])
        juzulhali = r.get("juzulhali", [])
        jadeed = r.get("jadeed", [])
        
        today_str = date.today().isoformat()
        is_absent = (
            not is_weekend
            and activity_date <= today_str
            and not murajat 
            and not juzulhali 
            and not jadeed 
            and not r.get("no_jadeed") 
            and not str((r.get("takhteet") or {}).get("murajat") or "").strip()
            and not str((r.get("takhteet") or {}).get("juzulhali") or "").strip()
            and not str((r.get("takhteet") or {}).get("jadeed") or "").strip()
        )
        
        is_weekend_empty = (
            is_weekend
            and not murajat 
            and not juzulhali 
            and not jadeed 
            and not r.get("no_jadeed") 
            and not str((r.get("takhteet") or {}).get("murajat") or "").strip()
            and not str((r.get("takhteet") or {}).get("juzulhali") or "").strip()
            and not str((r.get("takhteet") or {}).get("jadeed") or "").strip()
        )
        
        # 1. Render Absent Row
        if is_absent:
            cells = []
            cells.append(
                f'<td class="date-col">'
                f'  <div class="day-title">Day {date_num}</div>'
                f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                f'</td>'
            )
            cells.append(
                f'<td colspan="{cfg["colspan"]}" class="absent-cell">Absent / غائب</td>'
            )
            row_class = ' class="day-separator week-end-separator"' if wd == 6 else ' class="day-separator"'
            table_rows.append(f'<tr{row_class}>{"".join(cells)}</tr>')
            continue

        # 2. Render Empty Weekend Row
        if is_weekend_empty:
            cells = []
            cells.append(
                f'<td class="date-col">'
                f'  <div class="day-title">Day {date_num}</div>'
                f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                f'</td>'
            )
            weekend_label = "Saturday - Weekend" if wd == 5 else "Sunday - Weekend"
            cells.append(
                f'<td colspan="{cfg["colspan"]}" class="weekend-cell">{weekend_label}</td>'
            )
            row_class = ' class="day-separator week-end-separator"' if wd == 6 else ' class="day-separator"'
            table_rows.append(f'<tr{row_class}>{"".join(cells)}</tr>')
            continue

        # 3. Render Active Rows
        if report_type == "murajat":
            N_rows = max(len(murajat), 1)
            for sub_idx in range(N_rows):
                cells = []
                if sub_idx == 0:
                    cells.append(
                        f'<td class="date-col" rowspan="{N_rows}">'
                        f'  <div class="day-title">Day {date_num}</div>'
                        f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                        f'</td>'
                    )
                
                if sub_idx < len(murajat):
                    m = murajat[sub_idx]
                    surah_name = m.get("surah_name_ar") or m.get("surat") or ""
                    if surah_name and " - " in surah_name:
                        parts = surah_name.split(" - ")
                        surah_name = parts[1] if len(parts) > 1 else surah_name
                        
                    counts = m
                    talqeen = counts.get("talqeen", 0)
                    tanbeeh = counts.get("tanbeeh", 0)
                    irab = counts.get("irab", 0)
                    repeat = counts.get("repeat_mistake", 0)
                    mutashabehat = counts.get("mutashabehat", 0)
                    
                    mistake_badges = _format_mistake_badges(counts)
                    marks = m.get("marks", 0.0)
                    grade_badge = _format_grade_badge(marks)
                    
                    cells.append(f'<td class="text-left" style="font-weight: 600; font-size: 9pt;">{escape(surah_name)}</td>')
                    cells.append(f'<td>{talqeen}</td>')
                    cells.append(f'<td>{tanbeeh}</td>')
                    cells.append(f'<td>{irab}</td>')
                    cells.append(f'<td>{repeat}</td>')
                    cells.append(f'<td>{mutashabehat}</td>')
                    cells.append(f'<td style="text-align: left;">{mistake_badges}</td>')
                    cells.append(f'<td>{grade_badge}</td>')
                else:
                    cells.extend(['<td></td>'] * 8)
                
                is_last_sub = (sub_idx == N_rows - 1)
                row_class = ' class="day-separator week-end-separator"' if (is_last_sub and wd == 6) else (' class="day-separator"' if is_last_sub else '')
                table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")

        elif report_type == "juzulhali":
            N_rows = max(len(juzulhali), 1)
            for sub_idx in range(N_rows):
                cells = []
                if sub_idx == 0:
                    cells.append(
                        f'<td class="date-col" rowspan="{N_rows}">'
                        f'  <div class="day-title">Day {date_num}</div>'
                        f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                        f'</td>'
                    )
                
                if sub_idx < len(juzulhali):
                    j = juzulhali[sub_idx]
                    page = j.get("page_number", 0)
                    page_display = f"Page {page}" if page > 0 else "-"
                    
                    counts = j
                    talqeen = counts.get("talqeen", 0)
                    tanbeeh = counts.get("tanbeeh", 0)
                    irab = counts.get("irab", 0)
                    repeat = counts.get("repeat_mistake", 0)
                    mutashabehat = counts.get("mutashabehat", 0)
                    
                    mistake_badges = _format_mistake_badges(counts)
                    marks = j.get("marks", 0.0)
                    grade_badge = _format_grade_badge(marks)
                    
                    cells.append(f'<td style="font-weight: 600; font-size: 9pt;">{page_display}</td>')
                    cells.append(f'<td>{talqeen}</td>')
                    cells.append(f'<td>{tanbeeh}</td>')
                    cells.append(f'<td>{irab}</td>')
                    cells.append(f'<td>{repeat}</td>')
                    cells.append(f'<td>{mutashabehat}</td>')
                    cells.append(f'<td style="text-align: left;">{mistake_badges}</td>')
                    cells.append(f'<td>{grade_badge}</td>')
                else:
                    cells.extend(['<td></td>'] * 8)
                
                is_last_sub = (sub_idx == N_rows - 1)
                row_class = ' class="day-separator week-end-separator"' if (is_last_sub and wd == 6) else (' class="day-separator"' if is_last_sub else '')
                table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")

        elif report_type == "jadeed":
            if r.get("no_jadeed"):
                cells = []
                cells.append(
                    f'<td class="date-col">'
                    f'  <div class="day-title">Day {date_num}</div>'
                    f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                    f'</td>'
                )
                cells.append(f'<td colspan="4" style="font-style: italic; color: #7f8c8d; font-size: 8.5pt; text-align: center;">No Jadeed Lesson / لا جديد اليوم</td>')
                row_class = ' class="day-separator week-end-separator"' if wd == 6 else ' class="day-separator"'
                table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")
            else:
                N_rows = max(len(jadeed), 1)
                for sub_idx in range(N_rows):
                    cells = []
                    if sub_idx == 0:
                        cells.append(
                            f'<td class="date-col" rowspan="{N_rows}">'
                            f'  <div class="day-title">Day {date_num}</div>'
                            f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                            f'</td>'
                        )
                    
                    if sub_idx < len(jadeed):
                        jd = jadeed[sub_idx]
                        surah_name = jd.get("surah_name_ar") or jd.get("surat") or ""
                        if surah_name and " - " in surah_name:
                            parts = surah_name.split(" - ")
                            surah_name = parts[1] if len(parts) > 1 else surah_name
                            
                        page = jd.get("page_number", 0)
                        ayah = jd.get("ayah_number", 0)
                        volume = jd.get("volume") or "-"
                        
                        cells.append(f'<td class="text-left" style="font-weight: 600; font-size: 9pt;">{escape(surah_name)}</td>')
                        cells.append(f'<td>{page if page > 0 else "-"}</td>')
                        cells.append(f'<td>{ayah if ayah > 0 else "-"}</td>')
                        cells.append(f'<td>{escape(volume)}</td>')
                    else:
                        cells.extend(['<td></td>'] * 4)
                    
                    is_last_sub = (sub_idx == N_rows - 1)
                    row_class = ' class="day-separator week-end-separator"' if (is_last_sub and wd == 6) else (' class="day-separator"' if is_last_sub else '')
                    table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")

        elif report_type == "takhteet":
            cells = []
            cells.append(
                f'<td class="date-col">'
                f'  <div class="day-title">Day {date_num}</div>'
                f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                f'</td>'
            )
            
            t = r.get("takhteet") or {}
            m_hw = t.get("murajat") or ""
            j_hw = t.get("juzulhali") or ""
            jd_hw = t.get("jadeed") or ""
            
            cells.append(f'<td class="text-left" style="font-size: 8.5pt;">{escape(m_hw) if m_hw.strip() else "-"}</td>')
            cells.append(f'<td class="text-left" style="font-size: 8.5pt;">{escape(j_hw) if j_hw.strip() else "-"}</td>')
            cells.append(f'<td class="text-left" style="font-size: 8.5pt;">{escape(jd_hw) if jd_hw.strip() else "-"}</td>')
            
            row_class = ' class="day-separator week-end-separator"' if wd == 6 else ' class="day-separator"'
            table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")

    # Column headers depending on category
    if report_type == "murajat":
        thead_html = """
      <tr>
        <th style="width: 15%;">Date / Day</th>
        <th style="width: 20%;">Surah</th>
        <th style="width: 7%;">Talqeen</th>
        <th style="width: 7%;">Tanbeeh</th>
        <th style="width: 7%;">I'rab</th>
        <th style="width: 7%;">Repeat</th>
        <th style="width: 7%;">Mutash.</th>
        <th style="width: 24%;">Mistake Details</th>
        <th style="width: 10%;">Grade</th>
      </tr>
        """
    elif report_type == "juzulhali":
        thead_html = """
      <tr>
        <th style="width: 15%;">Date / Day</th>
        <th style="width: 20%;">Page</th>
        <th style="width: 7%;">Talqeen</th>
        <th style="width: 7%;">Tanbeeh</th>
        <th style="width: 7%;">I'rab</th>
        <th style="width: 7%;">Repeat</th>
        <th style="width: 7%;">Mutash.</th>
        <th style="width: 24%;">Mistake Details</th>
        <th style="width: 10%;">Grade</th>
      </tr>
        """
    elif report_type == "jadeed":
        thead_html = """
      <tr>
        <th style="width: 15%;">Date / Day</th>
        <th style="width: 40%;">Surah</th>
        <th style="width: 15%;">Page</th>
        <th style="width: 15%;">Ayah</th>
        <th style="width: 15%;">Volume</th>
      </tr>
        """
    else:  # takhteet
        thead_html = """
      <tr>
        <th style="width: 15%;">Date / Day</th>
        <th style="width: 28%;">Murajat Homework</th>
        <th style="width: 28%;">Juzulhali Homework</th>
        <th style="width: 29%;">Jadeed Homework</th>
      </tr>
        """

    return f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8"/>
  <title>{escape(cfg["title"])} - {escape(student_name)}</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 10mm 12mm 10mm 12mm;
    }}
    @media print {{
      .print-btn {{ display: none !important; }}
      * {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }}
    }}
    * {{
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
      box-sizing: border-box;
    }}
    .print-btn {{
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 9999;
      background: linear-gradient(135deg, #D4AF37 0%, #B88917 100%);
      color: #1E1A12;
      border: 2px solid {cfg["border"]};
      border-radius: 12px;
      padding: 10px 24px;
      font-size: 10.5pt;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(212,175,55,0.45);
      letter-spacing: 0.4px;
      transition: all 0.2s ease;
    }}
    .print-btn:hover {{
      background: linear-gradient(135deg, #e0bf4a 0%, #c99b1e 100%);
      transform: translateY(-1px);
    }}
    body {{
      font-family: "Segoe UI", Arial, sans-serif;
      direction: ltr;
      color: #2d3748;
      font-size: 8.5pt;
      line-height: 1.4;
      margin: 0;
      padding: 0;
      background-color: #ffffff;
    }}
    
    /* Stats cards styling */
    .stats-container {{
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      width: 100%;
    }}
    .stat-card {{
      flex: 1;
      background: #fdfcf9;
      border: 1px solid #e2dccf;
      border-left: 4px solid {cfg["border"]};
      border-radius: 8px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }}
    .stat-title {{
      font-size: 7.5pt;
      font-weight: 600;
      color: #718096;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .stat-value {{
      font-size: 13.5pt;
      font-weight: bold;
      color: {cfg["border"]};
    }}

    /* Table styling */
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin-top: 5px;
      border: 1.5px solid {cfg["border"]};
    }}
    th {{
      color: #ffffff;
      font-weight: bold;
      border: 1px solid {cfg["border"]};
      font-size: 9pt;
      padding: 10px 8px;
      text-align: center;
      vertical-align: middle;
      background: {cfg["bg"]};
    }}
    td {{
      border: 1px solid #e2e8f0;
      padding: 7px 8px;
      vertical-align: middle;
      font-size: 8.5pt;
      text-align: center;
      word-wrap: break-word;
      word-break: break-word;
      overflow-wrap: break-word;
    }}
    
    .date-col {{
      background-color: #f7f5f0 !important;
      text-align: left !important;
      padding: 8px 12px !important;
      border-right: 2.5px solid {cfg["border"]} !important;
    }}
    .day-title {{
      font-weight: bold;
      font-size: 9.5pt;
      color: {cfg["border"]};
    }}
    .day-subtitle {{
      font-size: 7.5pt;
      color: #718096;
      margin-top: 2px;
    }}
    
    .absent-cell {{
      background-color: #fff5f5 !important;
      color: #e53e3e !important;
      font-weight: bold;
      font-size: 9.5pt;
      text-align: center;
    }}
    .weekend-cell {{
      background-color: #f7fafc !important;
      color: #4a5568 !important;
      font-weight: bold;
      font-size: 9.5pt;
      text-align: center;
    }}
    
    /* Tag Pills styling */
    .badge {{
      display: inline-block;
      padding: 2.5px 7px;
      font-size: 7.5pt;
      font-weight: bold;
      border-radius: 20px;
      margin: 2px;
      white-space: nowrap;
    }}
    .badge-ahkam {{
      background-color: #fff5f5;
      color: #9b2c2c;
      border: 1.2px solid #fed7d7;
    }}
    .badge-makhraj {{
      background-color: #ebf8ff;
      color: #2b6cb0;
      border: 1.2px solid #bee3f8;
      font-family: 'Amiri', 'Traditional Arabic', serif;
      font-size: 9pt;
    }}
    
    /* Grade badges */
    .grade-badge {{
      display: inline-block;
      padding: 4px 10px;
      font-size: 9pt;
      font-weight: bold;
      border-radius: 6px;
      text-align: center;
    }}
    .grade-excellent {{
      background-color: #c6f6d5;
      color: #22543d;
      border: 1px solid #98e2b1;
    }}
    .grade-passing {{
      background-color: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }}
    .grade-warning {{
      background-color: #fed7d7;
      color: #9b2c2c;
      border: 1px solid #feb2b2;
    }}

    .text-left {{
      text-align: left;
      padding-left: 10px;
    }}
    .day-separator td {{
      border-bottom: 2px solid {cfg["border"]} !important;
    }}
    .week-end-separator td {{
      border-bottom: 4px double {cfg["border"]} !important;
    }}
    .muted {{
      color: #a0aec0;
      font-style: italic;
    }}
  </style>
</head>
<body>
  <!-- Header Banner -->
  <div style="
    background: {cfg["bg"]};
    border-bottom: 4px solid #D4AF37;
    padding: 14px 20px;
    margin-bottom: 15px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  ">
    <div style="text-align: left; width: 30%;">
      <div style="color: #D4AF37; font-size: 7.5pt; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Student</div>
      <div style="color: #ffffff; font-size: 11pt; font-weight: 800; margin-top: 1px;">{escape(student_name)}</div>
    </div>
    <div style="text-align: center; flex: 1; padding: 0 10px;">
      <div style="color: #D4AF37; font-size: 8.5pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div style="color: #ffffff; font-size: 13.5pt; font-weight: 950; letter-spacing: 0.5px; margin-top: 2px;">{escape(cfg["title"])}</div>
    </div>
    <div style="text-align: right; width: 30%;">
      <div style="color: #D4AF37; font-size: 7.5pt; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">Month</div>
      <div style="color: #ffffff; font-size: 11pt; font-weight: 800; margin-top: 1px;">{escape(month_year_str)}</div>
    </div>
  </div>

  <!-- Summary Statistics Grid -->
  {stats_html}

  <!-- Report Data Table -->
  <table>
    <thead>
      {thead_html}
    </thead>
    <tbody>
      {"".join(table_rows)}
    </tbody>
  </table>

  <!-- Floating Print Button -->
  <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>

</body>
</html>
"""


def export_html_to_pdf_bytes(html: str) -> bytes:
    """
    Uses Playwright (Chromium) for reliable single-page A4 portrait PDF export.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        pdf = page.pdf(
            prefer_css_page_size=True,
            print_background=True
        )
        browser.close()
        return pdf
