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
    "mad_tabaiee": "M. Tabai.",
    "ikhfa_shafawi": "Ikh. Shaf.",
    "iqlab": "Iqlab"
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

SIPARA_TO_SURAH = {
    1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8,
    11: 9, 12: 11, 13: 12, 14: 15, 15: 17, 16: 18, 17: 21, 18: 23, 19: 25, 20: 27,
    21: 29, 22: 33, 23: 36, 24: 39, 25: 41, 26: 46, 27: 51, 28: 58, 29: 67, 30: 78
}

SIPARA_NAMES = {
    1: "Sipara 1 (الم)", 2: "Sipara 2 (سيقول)", 3: "Sipara 3 (تلك الرسل)", 4: "Sipara 4 (لن تنالوا)",
    5: "Sipara 5 (والمحصنات)", 6: "Sipara 6 (لا يحب الله)", 7: "Sipara 7 (وإذا سمعوا)", 8: "Sipara 8 (ولو أننا)",
    9: "Sipara 9 (قال الملأ)", 10: "Sipara 10 (واعلموا)", 11: "Sipara 11 (يعتذرون)", 12: "Sipara 12 (وما من دابة)",
    13: "Sipara 13 (وما أبرئ)", 14: "Sipara 14 (ربما)", 15: "Sipara 15 (سبحان الذي)", 16: "Sipara 16 (قال ألم)",
    17: "Sipara 17 (اقترب)", 18: "Sipara 18 (قد أفلح)", 19: "Sipara 19 (وقال الذين)", 20: "Sipara 20 (أمن خلق)",
    21: "Sipara 21 (اتل ما أوحي)", 22: "Sipara 22 (ومن يقنت)", 23: "Sipara 23 (وما لي)", 24: "Sipara 24 (فمن أظلم)",
    25: "Sipara 25 (إليه يرد)", 26: "Sipara 26 (حم)", 27: "Sipara 27 (قال فما خطبكم)", 28: "Sipara 28 (قد سمع الله)",
    29: "Sipara 29 (تبارك الذي)", 30: "Sipara 30 (عم يتساءلون)"
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
            lbl = f"{label}" if val == 1 else f"{label} ({val})"
            badges.append(
                f'<span class="badge badge-ahkam">{lbl}</span>'
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


def _get_takhteet_values(t: Optional[Dict[str, Any]]) -> Tuple[str, str, str]:
    if not t or not isinstance(t, dict):
        return "", "", ""
    m = t.get("murajat") or t.get("murajat_text") or t.get("murajat_text_raw") or t.get("murajat_text_clean") or ""
    j = t.get("juzulhali") or t.get("juzulhali_text") or t.get("juzulhali_text_raw") or t.get("juzulhali_text_clean") or ""
    jd = t.get("jadeed") or t.get("jadeed_text") or t.get("jadeed_text_raw") or t.get("jadeed_text_clean") or ""
    return str(m), str(j), str(jd)


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
        t_m, t_j, t_jd = _get_takhteet_values(r.get("takhteet"))
        is_present = bool(murajat or juzulhali or jadeed or not (
            r.get("no_jadeed", True)
            and not t_m.strip()
            and not t_j.strip()
            and not t_jd.strip()
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
            if t_m.strip() or t_j.strip() or t_jd.strip():
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
        t_m, t_j, t_jd = _get_takhteet_values(r.get("takhteet"))
        is_absent = (
            not is_weekend
            and activity_date <= today_str
            and not murajat 
            and not juzulhali 
            and not jadeed 
            and not r.get("no_jadeed") 
            and not t_m.strip()
            and not t_j.strip()
            and not t_jd.strip()
        )
        
        is_weekend_empty = (
            is_weekend
            and not murajat 
            and not juzulhali 
            and not jadeed 
            and not r.get("no_jadeed") 
            and not t_m.strip()
            and not t_j.strip()
            and not t_jd.strip()
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
                        
                    page_val = m.get("page_number")
                    try:
                        page = int(page_val) if page_val is not None else 0
                    except (ValueError, TypeError):
                        page = 0
                    surah_id = m.get("surah_id")
                    if page in range(1, 31) and (surah_id == SIPARA_TO_SURAH.get(page) or not surah_name or surah_name == "Surah"):
                        surah_display = SIPARA_NAMES.get(page, f"Sipara {page}")
                    elif page > 0:
                        surah_display = f"{surah_name} (p. {page})"
                    else:
                        surah_display = surah_name
                        
                    counts = m
                    talqeen = counts.get("talqeen", 0)
                    tanbeeh = counts.get("tanbeeh", 0)
                    irab = counts.get("irab", 0)
                    repeat = counts.get("repeat_mistake", 0)
                    mutashabehat = counts.get("mutashabehat", 0)
                    
                    mistake_badges = _format_mistake_badges(counts)
                    marks = m.get("marks", 0.0)
                    grade_badge = _format_grade_badge(marks)
                    dur_sec = m.get("duration_seconds", 0)
                    if dur_sec and int(dur_sec) > 0:
                        dur_m = int(dur_sec) // 60
                        dur_s = int(dur_sec) % 60
                        is_over = bool(m.get("time_exceeded") or int(dur_sec) > 600)
                        bg = "#fee2e2" if is_over else "#e0f2fe"
                        fg = "#dc2626" if is_over else "#0369a1"
                        grade_badge += f'<div style="font-size:7pt; font-weight:bold; color:{fg}; background:{bg}; border-radius:3px; padding:1px 4px; margin-top:2px;">⏱️ {dur_m}m {dur_s:02d}s</div>'
                    
                    cells.append(f'<td class="text-left" style="font-weight: 600; font-size: 9pt;">{escape(surah_display)}</td>')
                    cells.append(f'<td>{talqeen}</td>')
                    cells.append(f'<td>{tanbeeh}</td>')
                    cells.append(f'<td>{irab}</td>')
                    # cells.append(f'<td>{repeat}</td>')
                    # cells.append(f'<td>{mutashabehat}</td>')
                    cells.append(f'<td style="text-align: left;">{mistake_badges}</td>')
                    cells.append(f'<td>{grade_badge}</td>')
                else:
                    cells.extend(['<td></td>'] * 6)
                
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
                    page_val = j.get("page_number")
                    try:
                        page = int(page_val) if page_val is not None else 0
                    except (ValueError, TypeError):
                        page = 0
                    surah_name = j.get("surah_name_ar") or j.get("surat") or ""
                    if surah_name and " - " in surah_name:
                        parts = surah_name.split(" - ")
                        surah_name = parts[1] if len(parts) > 1 else surah_name
                    
                    surah_id = j.get("surah_id")
                    if surah_id and page in range(1, 31) and surah_id == SIPARA_TO_SURAH.get(page):
                        page_display = SIPARA_NAMES.get(page, f"Sipara {page}")
                    elif surah_name and surah_name != "Surah":
                        page_display = f"{surah_name} (p. {page})"
                    else:
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
                    dur_sec = j.get("duration_seconds", 0)
                    if dur_sec and int(dur_sec) > 0:
                        dur_m = int(dur_sec) // 60
                        dur_s = int(dur_sec) % 60
                        is_over = bool(j.get("time_exceeded") or int(dur_sec) > 900)
                        bg = "#fee2e2" if is_over else "#fef3c7"
                        fg = "#dc2626" if is_over else "#b45309"
                        grade_badge += f'<div style="font-size:7pt; font-weight:bold; color:{fg}; background:{bg}; border-radius:3px; padding:1px 4px; margin-top:2px;">⏱️ {dur_m}m {dur_s:02d}s</div>'
                    
                    cells.append(f'<td class="text-left" style="font-weight: 600; font-size: 9pt;">{escape(page_display)}</td>')
                    cells.append(f'<td>{talqeen}</td>')
                    cells.append(f'<td>{tanbeeh}</td>')
                    cells.append(f'<td>{irab}</td>')
                    # cells.append(f'<td>{repeat}</td>')
                    # cells.append(f'<td>{mutashabehat}</td>')
                    cells.append(f'<td style="text-align: left;">{mistake_badges}</td>')
                    cells.append(f'<td>{grade_badge}</td>')
                else:
                    cells.extend(['<td></td>'] * 6)
                
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
                reasons = r.get("no_jadeed_reasons") or []
                if not reasons and r.get("no_jadeed_details"):
                    jd_det = r.get("no_jadeed_details")
                    if jd_det.get("weak_hifz"): reasons.append("Weak Hifz")
                    if jd_det.get("airab_mistakes"): reasons.append("Airab Mistakes")
                    if jd_det.get("time_exceeded"): reasons.append("Time Exceeded")
                    if jd_det.get("weak_murajat"): reasons.append("Weak Murajat")
                    if jd_det.get("weak_juzulhali"): reasons.append("Weak Juz'ul Hali")
                if reasons:
                    badge_spans = " ".join([f'<span style="display:inline-block; font-size:7pt; font-weight:600; color:#9a3412; background:#ffedd5; border:1px solid #fed7aa; border-radius:3px; padding:1px 4px; margin:1px;">{escape(rs)}</span>' for rs in reasons])
                    cells.append(f'<td colspan="4" style="color: #7f8c8d; font-size: 8.5pt; text-align: center;"><em>No Jadeed Lesson / لا جديد اليوم</em><div style="margin-top:2px;">{badge_spans}</div></td>')
                else:
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
                            
                        page_val = jd.get("page_number")
                        try:
                            page = int(page_val) if page_val is not None else 0
                        except (ValueError, TypeError):
                            page = 0
                        ayah_val = jd.get("ayah_number")
                        try:
                            ayah = int(ayah_val) if ayah_val is not None else 0
                        except (ValueError, TypeError):
                            ayah = 0
                        volume = jd.get("volume") or "-"
                        volume_str = escape(volume)
                        flag_badges = []
                        if jd.get("weak_hifz"):
                            flag_badges.append('<span style="background:#fff3cd; color:#856404; font-size:7pt; padding:1px 4px; border-radius:3px; font-weight:bold; margin-left:3px;">Weak</span>')
                        if jd.get("airab_mistakes"):
                            flag_badges.append('<span style="background:#f8d7da; color:#721c24; font-size:7pt; padding:1px 4px; border-radius:3px; font-weight:bold; margin-left:3px;">I\'rab</span>')
                        dur_sec = jd.get("duration_seconds", 0)
                        if jd.get("time_exceeded") or (dur_sec and int(dur_sec) > 300):
                            flag_badges.append('<span style="background:#ffedd5; color:#c2410c; font-size:7pt; padding:1px 4px; border-radius:3px; font-weight:bold; margin-left:3px;">Overtime</span>')
                        if jd.get("weak_murajat"):
                            flag_badges.append('<span style="background:#dbeafe; color:#1e40af; font-size:7pt; padding:1px 4px; border-radius:3px; font-weight:bold; margin-left:3px;">Weak Mur</span>')
                        if jd.get("weak_juzulhali"):
                            flag_badges.append('<span style="background:#f3e8ff; color:#6b21a8; font-size:7pt; padding:1px 4px; border-radius:3px; font-weight:bold; margin-left:3px;">Weak JH</span>')
                        if dur_sec and int(dur_sec) > 0:
                            dur_m = int(dur_sec) // 60
                            dur_s = int(dur_sec) % 60
                            flag_badges.append(f'<span style="background:#e0f2fe; color:#0369a1; font-size:7pt; padding:1px 4px; border-radius:3px; font-weight:bold; margin-left:3px;">⏱️{dur_m}:{dur_s:02d}</span>')
                        if flag_badges:
                            volume_str += " " + "".join(flag_badges)
                        
                        cells.append(f'<td class="text-left" style="font-weight: 600; font-size: 9pt;">{escape(surah_name)}</td>')
                        cells.append(f'<td>{page if page > 0 else "-"}</td>')
                        cells.append(f'<td>{ayah if ayah > 0 else "-"}</td>')
                        cells.append(f'<td>{volume_str}</td>')
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
            
            m_hw, j_hw, jd_hw = _get_takhteet_values(r.get("takhteet"))
            
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
        <th style="width: 25%;">Sipara / Surah</th>
        <th style="width: 8%;">Talqeen</th>
        <th style="width: 8%;">Tanbeeh</th>
        <th style="width: 8%;">I'rab</th>
        <!-- <th style="width: 7%;">Repeat</th> -->
        <!-- <th style="width: 7%;">Mutash.</th> -->
        <th style="width: 26%;">Mistake Details</th>
        <th style="width: 10%;">Grade</th>
      </tr>
        """
    elif report_type == "juzulhali":
        thead_html = """
      <tr>
        <th style="width: 15%;">Date / Day</th>
        <th style="width: 25%;">Sipara / Page</th>
        <th style="width: 8%;">Talqeen</th>
        <th style="width: 8%;">Tanbeeh</th>
        <th style="width: 8%;">I'rab</th>
        <!-- <th style="width: 7%;">Repeat</th> -->
        <!-- <th style="width: 7%;">Mutash.</th> -->
        <th style="width: 26%;">Mistake Details</th>
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


def build_current_jadeed_report_html(
    student_name: str,
    current_entry: Optional[Dict[str, Any]],
    all_students_data: List[Dict[str, Any]]
) -> str:
    """
    Generates a beautifully-designed HTML report displaying:
    1. A prominent card showing the student's current memorization position (latest Jadeed).
    2. A comprehensive class-wide table showing every student's current Jadeed.
    """
    # 1. Format Selected Student's Current Jadeed Card
    card_html = ""
    if not current_entry:
        card_html = """
        <div class="current-card no-entry">
            <h3>No Jadeed Recorded</h3>
            <p>This student does not have any Jadeed entries logged in the database yet.</p>
        </div>
        """
    elif current_entry.get("no_jadeed"):
        card_html = f"""
        <div class="current-card no-entry">
            <h3>Marked 'No Jadeed'</h3>
            <p>The student was marked as "No Jadeed today" on their last session date: <strong>{current_entry.get('activity_date')}</strong>.</p>
        </div>
        """
    else:
        surah = current_entry.get("surahs") or {}
        if isinstance(surah, list):
            surah = surah[0] if surah else {}
        surah_en = surah.get("name_en", "?")
        surah_ar = surah.get("name_ar", "")
        surah_num = surah.get("number", "?")
        
        pg_val = current_entry.get("page_number")
        page = pg_val if pg_val is not None else "-"
        ay_val = current_entry.get("ayah_number")
        ayah = ay_val if ay_val is not None else "-"
        volume = current_entry.get("volume", "-")
        date_recited = current_entry.get("activity_date", "-")
        
        card_html = f"""
        <div class="current-card">
            <div class="card-header">
                <span class="card-badge">Current Position / الموقع الحالي</span>
                <h2>Surah {surah_num}: {escape(surah_en)} <span class="arabic-text">{escape(surah_ar)}</span></h2>
            </div>
            <div class="card-grid">
                <div class="grid-item">
                    <span class="grid-label">Page / الصفحة</span>
                    <span class="grid-value">{page}</span>
                </div>
                <div class="grid-item">
                    <span class="grid-label">Ayah / الآية</span>
                    <span class="grid-value">{ayah}</span>
                </div>
                <div class="grid-item">
                    <span class="grid-label">Volume / المقدار</span>
                    <span class="grid-value">{escape(volume)}</span>
                </div>
                <div class="grid-item">
                    <span class="grid-label">Recited Date / تاريخ التلاوة</span>
                    <span class="grid-value">{date_recited}</span>
                </div>
            </div>
        </div>
        """

    # 2. Render Class Overview Table
    table_rows = []
    for idx, s in enumerate(all_students_data):
        is_current = s["student_name"] == student_name
        row_class = ' class="selected-student-row"' if is_current else ""
        name_display = f"⭐ {escape(s['student_name'])}" if is_current else escape(s['student_name'])
        
        status_badge = ""
        if s["status"] == "Active":
            status_badge = '<span class="status-pill active-status">Active</span>'
        elif s["status"] == "Marked 'No Jadeed'":
            status_badge = '<span class="status-pill warning-status">No Jadeed</span>'
        else:
            status_badge = '<span class="status-pill muted-status">None</span>'
            
        table_rows.append(f"""
        <tr{row_class}>
            <td>{idx + 1}</td>
            <td class="text-left" style="font-weight: 600;">{name_display}</td>
            <td>{s['last_date']}</td>
            <td class="text-left">{escape(s['surah'])}</td>
            <td>{s['page']}</td>
            <td>{s['ayah']}</td>
            <td>{escape(s['volume'])}</td>
            <td>{status_badge}</td>
        </tr>
        """)

    theme_bg = "linear-gradient(135deg, #0e6b50 0%, #114e3b 100%)"
    theme_border = "#0e6b50"
    
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Current Jadeed Overview - {escape(student_name)}</title>
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
      box-sizing: border-box;
    }}
    body {{
      font-family: "Segoe UI", Arial, sans-serif;
      color: #2d3748;
      font-size: 8.5pt;
      line-height: 1.4;
      margin: 0;
      padding: 0;
      background-color: #ffffff;
    }}
    
    /* Header Banner */
    .header-banner {{
      background: {theme_bg};
      border-bottom: 4px solid #D4AF37;
      padding: 14px 20px;
      margin-bottom: 20px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .header-left, .header-right {{
      width: 30%;
    }}
    .header-left {{ text-align: left; }}
    .header-right {{ text-align: right; }}
    .header-center {{
      text-align: center;
      flex: 1;
    }}
    .header-label {{
      color: #D4AF37;
      font-size: 7.5pt;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}
    .header-value {{
      color: #ffffff;
      font-size: 11pt;
      font-weight: 800;
      margin-top: 1px;
    }}
    .header-title {{
      color: #ffffff;
      font-size: 13.5pt;
      font-weight: 950;
      letter-spacing: 0.5px;
      margin-top: 2px;
    }}
    
    /* Current Jadeed Card */
    .current-card {{
      background: #fcfbfa;
      border: 2px solid #e2dccf;
      border-top: 6px solid #D4AF37;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 25px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }}
    .current-card.no-entry {{
      border-top-color: #e53e3e;
      text-align: center;
      padding: 30px;
    }}
    .current-card.no-entry h3 {{
      color: #e53e3e;
      margin-top: 0;
      font-size: 13pt;
    }}
    .current-card.no-entry p {{
      color: #718096;
      font-size: 9.5pt;
      margin-bottom: 0;
    }}
    .card-header {{
      border-bottom: 1.5px solid #e2e8f0;
      padding-bottom: 12px;
      margin-bottom: 16px;
    }}
    .card-badge {{
      display: inline-block;
      background-color: #e6fffa;
      color: #0e6b50;
      font-weight: 800;
      font-size: 8pt;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
      border: 1px solid #b2f5ea;
    }}
    .card-header h2 {{
      margin: 0;
      font-size: 14pt;
      color: #0e6b50;
      font-weight: 800;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .arabic-text {{
      font-family: "Amiri", "Traditional Arabic", serif;
      font-size: 18pt;
      color: #1a202c;
      font-weight: normal;
    }}
    .card-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 15px;
    }}
    .grid-item {{
      background: #ffffff;
      border: 1.5px solid #edf2f7;
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
    }}
    .grid-label {{
      font-size: 7.5pt;
      font-weight: 600;
      color: #a0aec0;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .grid-value {{
      font-size: 12pt;
      font-weight: bold;
      color: #2d3748;
    }}
    
    /* Table styling */
    h3.section-title {{
      font-size: 11pt;
      font-weight: 800;
      color: #0e6b50;
      margin: 0 0 10px 0;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      border: 1.5px solid {theme_border};
    }}
    th {{
      color: #ffffff;
      font-weight: bold;
      border: 1px solid {theme_border};
      font-size: 9pt;
      padding: 10px 8px;
      text-align: center;
      vertical-align: middle;
      background: {theme_bg};
    }}
    td {{
      border: 1px solid #e2e8f0;
      padding: 8px 8px;
      vertical-align: middle;
      font-size: 8.5pt;
      text-align: center;
    }}
    .selected-student-row {{
      background-color: #e6fffa !important;
      border-top: 2px solid #319795 !important;
      border-bottom: 2px solid #319795 !important;
    }}
    .selected-student-row td {{
      font-weight: bold;
      color: #004b39;
    }}
    .text-left {{
      text-align: left;
      padding-left: 12px;
    }}
    
    /* Status pills */
    .status-pill {{
      display: inline-block;
      padding: 2px 8px;
      font-size: 7.5pt;
      font-weight: bold;
      border-radius: 4px;
      text-align: center;
    }}
    .active-status {{
      background-color: #c6f6d5;
      color: #22543d;
      border: 1px solid #98e2b1;
    }}
    .warning-status {{
      background-color: #feebc8;
      color: #744210;
      border: 1px solid #fbd38d;
    }}
    .muted-status {{
      background-color: #edf2f7;
      color: #4a5568;
      border: 1px solid #e2e8f0;
    }}
    
    /* Print Button */
    .print-btn {{
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 9999;
      background: linear-gradient(135deg, #D4AF37 0%, #B88917 100%);
      color: #1E1A12;
      border: 2px solid {theme_border};
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
  </style>
</head>
<body>
  <!-- Header Banner -->
  <div class="header-banner">
    <div class="header-left">
      <div class="header-label">Selected Student</div>
      <div class="header-value">{escape(student_name)}</div>
    </div>
    <div class="header-center">
      <div class="header-label" style="letter-spacing: 1.5px;">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div class="header-title">Current Memorization Position</div>
    </div>
    <div class="header-right">
      <div class="header-label">Class Year</div>
      <div class="header-value">2026 Mukhayyam</div>
    </div>
  </div>

  <!-- Prominent Card -->
  {card_html}

  <!-- Section Title -->
  <h3 class="section-title">👥 Class-Wide Jadeed Progress Overview</h3>

  <!-- Class Table -->
  <table>
    <thead>
      <tr>
        <th style="width: 5%;">S.No</th>
        <th style="width: 25%;">Student Name</th>
        <th style="width: 15%;">Last Recited Date</th>
        <th style="width: 25%;">Current Surah</th>
        <th style="width: 8%;">Page</th>
        <th style="width: 8%;">Ayah</th>
        <th style="width: 8%;">Volume</th>
        <th style="width: 8%;">Status</th>
      </tr>
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


def build_collective_attendance_report_html(data: Dict[str, Any]) -> str:
    """
    Generates a beautifully-designed collective (class-wide) monthly attendance HTML report.
    """
    import calendar
    from datetime import datetime
    
    year = data["year"]
    month = data["month"]
    students = data["students"]
    days = data["days"]
    
    month_name = calendar.month_name[month]
    month_year_str = f"{month_name} {year}"
    
    # Calculate class-wide stats
    total_students = len(students)
    school_days = students[0]["stats"]["school_days"] if students else 0
    
    avg_sum = 0.0
    perfect_count = 0
    warning_count = 0
    
    for s in students:
        rate = s["stats"]["attendance_rate"]
        avg_sum += rate
        if rate >= 99.9:
            perfect_count += 1
        elif rate < 85.0:
            warning_count += 1
            
    class_avg = (avg_sum / total_students) if total_students > 0 else 100.0
    
    # KPI Stats Cards HTML
    stats_html = f"""
    <div class="stats-container">
        <div class="stat-card" style="border-left-color: #2b6cb0;">
            <span class="stat-title">Class Average Attendance</span>
            <span class="stat-value" style="color: #2b6cb0;">{class_avg:.1f}%</span>
        </div>
        <div class="stat-card" style="border-left-color: #4a5568;">
            <span class="stat-title">Total Students</span>
            <span class="stat-value" style="color: #4a5568;">{total_students}</span>
        </div>
        <div class="stat-card" style="border-left-color: #2f855a;">
            <span class="stat-title">Perfect Attendance (100%)</span>
            <span class="stat-value" style="color: #2f855a;">{perfect_count} {"Student" if perfect_count == 1 else "Students"}</span>
        </div>
        <div class="stat-card" style="border-left-color: #c53030;">
            <span class="stat-title">Needs Attention (&lt;85%)</span>
            <span class="stat-value" style="color: #c53030;">{warning_count} {"Student" if warning_count == 1 else "Students"}</span>
        </div>
    </div>
    """
    
    # Table headers: Days 1 to last_day
    day_headers = []
    for d_str in days:
        day_num = int(d_str[-2:])
        try:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            wd_name = dt.strftime("%a")[0] # M, T, W...
        except Exception:
            wd_name = ""
        day_headers.append(
            f'<th class="day-header-col" title="{d_str}">{day_num}<br/><span style="font-size: 6.5pt; font-weight: normal; opacity: 0.75;">{wd_name}</span></th>'
        )
        
    thead_html = f"""
    <tr>
      <th style="width: 35px;">S.No</th>
      <th style="width: 140px; text-align: left; padding-left: 8px;">Student Name</th>
      {"".join(day_headers)}
      <th style="width: 45px;" title="Total Present Days">Pres</th>
      <th style="width: 45px;" title="Total Absent Days">Abs</th>
      <th style="width: 55px;">Rate %</th>
    </tr>
    """
    
    # Table rows
    table_rows = []
    for idx, s in enumerate(students):
        row_cells = []
        row_cells.append(f'<td>{idx + 1}</td>')
        row_cells.append(f'<td class="text-left" style="font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{escape(s["full_name"])}</td>')
        
        attendance = s["attendance"]
        for d_str in days:
            day_info = attendance.get(d_str, {"status": "Future", "details": ""})
            status = day_info["status"]
            details = day_info["details"] or ""
            
            cell_class = ""
            cell_content = ""
            
            if status == "Present":
                cell_class = "present-cell"
                cell_content = "✔"
            elif status == "Absent":
                cell_class = "absent-cell"
                cell_content = "❌"
            elif status == "Weekend":
                cell_class = "weekend-cell"
                cell_content = "W"
            else: # Future
                cell_class = "future-cell"
                cell_content = ""
                
            row_cells.append(
                f'<td class="status-cell {cell_class}" title="{escape(details)}">{cell_content}</td>'
            )
            
        stats = s["stats"]
        tot_present = stats["present_days"] + stats["extra_weekend_days"]
        tot_absent = stats["absent_days"]
        rate = stats["attendance_rate"]
        
        if rate >= 95.0:
            rate_badge_class = "rate-excellent"
        elif rate >= 85.0:
            rate_badge_class = "rate-passing"
        else:
            rate_badge_class = "rate-warning"
            
        row_cells.append(f'<td style="font-weight: 600; color: #2e7d32;">{tot_present}</td>')
        row_cells.append(f'<td style="font-weight: 600; color: #c62828;">{tot_absent}</td>')
        row_cells.append(f'<td><span class="rate-badge {rate_badge_class}">{rate:.1f}%</span></td>')
        
        table_rows.append(f'<tr>{"".join(row_cells)}</tr>')
        
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Collective Attendance Report - {escape(month_year_str)}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    @page {{
      size: A4 landscape;
      margin: 8mm 10mm 8mm 10mm;
    }}
    @media print {{
      .print-btn {{ display: none !important; }}
      * {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }}
    }}
    * {{
      box-sizing: border-box;
      font-family: 'Inter', "Segoe UI", Arial, sans-serif;
    }}
    body {{
      color: #2d3748;
      font-size: 8pt;
      line-height: 1.3;
      margin: 0;
      padding: 0;
      background-color: #ffffff;
    }}
    .print-btn {{
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 9999;
      background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
      color: #ffffff;
      border: none;
      border-radius: 8px;
      padding: 8px 20px;
      font-size: 9.5pt;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(30,60,114,0.3);
      transition: all 0.2s ease;
    }}
    .print-btn:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(30,60,114,0.4);
    }}
    
    /* Header styling */
    .header-banner {{
      background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
      border-bottom: 4px solid #D4AF37;
      padding: 10px 16px;
      margin-bottom: 12px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #ffffff;
    }}
    .header-title {{
      font-size: 12.5pt;
      font-weight: 800;
      margin: 0;
    }}
    .header-subtitle {{
      font-size: 7.5pt;
      color: #D4AF37;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    
    /* Stats cards */
    .stats-container {{
      display: flex;
      gap: 10px;
      margin-bottom: 12px;
      width: 100%;
    }}
    .stat-card {{
      flex: 1;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #1e3c72;
      border-radius: 6px;
      padding: 8px 12px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .stat-title {{
      font-size: 7pt;
      font-weight: 600;
      color: #718096;
      margin-bottom: 2px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .stat-value {{
      font-size: 11pt;
      font-weight: 800;
    }}
    
    /* Grid Table styling */
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin-top: 5px;
      border: 1.5px solid #1e3c72;
    }}
    th {{
      color: #ffffff;
      font-weight: bold;
      border: 1px solid #1e3c72;
      font-size: 8pt;
      padding: 6px 4px;
      text-align: center;
      vertical-align: middle;
      background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }}
    td {{
      border: 1px solid #e2e8f0;
      padding: 5px 4px;
      vertical-align: middle;
      font-size: 7.5pt;
      text-align: center;
    }}
    .text-left {{
      text-align: left;
      padding-left: 8px;
    }}
    
    /* Cell statuses */
    .status-cell {{
      font-weight: bold;
      font-size: 7pt;
      transition: all 0.15s ease;
      cursor: help;
    }}
    .present-cell {{
      background-color: #e6fffa !important;
      color: #00796b !important;
    }}
    .absent-cell {{
      background-color: #ffeeee !important;
      color: #c62828 !important;
    }}
    .weekend-cell {{
      background-color: #f7fafc !important;
      color: #a0aec0 !important;
      font-weight: normal;
    }}
    .future-cell {{
      background-color: #ffffff !important;
      color: #e2e8f0 !important;
    }}
    
    /* Header day columns */
    .day-header-col {{
      font-size: 7.5pt;
      line-height: 1.1;
    }}
    
    /* Attendance Rate Badges */
    .rate-badge {{
      display: inline-block;
      padding: 2px 6px;
      font-size: 7.5pt;
      font-weight: bold;
      border-radius: 4px;
      text-align: center;
    }}
    .rate-excellent {{
      background-color: #c6f6d5;
      color: #22543d;
    }}
    .rate-passing {{
      background-color: #fef3c7;
      color: #92400e;
    }}
    .rate-warning {{
      background-color: #fed7d7;
      color: #9b2c2c;
    }}
  </style>
</head>
<body>
  <!-- Header Banner -->
  <div class="header-banner">
    <div>
      <div class="header-subtitle">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div class="header-title">Collective Attendance Report (حضور الطلاب)</div>
    </div>
    <div style="text-align: right;">
      <div class="header-subtitle">Report Month</div>
      <div style="font-size: 11pt; font-weight: bold; margin-top: 1px;">{escape(month_year_str)}</div>
    </div>
  </div>

  <!-- Summary Statistics Grid -->
  {stats_html}

  <!-- Report Data Grid Table -->
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


_quran_metadata = None


def get_quran_page(surah_num: int, ayah_num: int) -> int:
    global _quran_metadata
    if _quran_metadata is None:
        try:
            import json
            import os
            path = os.path.join(os.path.dirname(__file__), "quran_metadata.json")
            with open(path, "r", encoding="utf-8") as f:
                _quran_metadata = json.load(f)
        except Exception:
            _quran_metadata = {}
            
    s_str = str(surah_num)
    if _quran_metadata and "surahs" in _quran_metadata and s_str in _quran_metadata["surahs"]:
        pages_dict = _quran_metadata["surahs"][s_str].get("pages", {})
        for page_num_str, ayahs in pages_dict.items():
            if ayah_num in ayahs or str(ayah_num) in ayahs:
                return int(page_num_str)
    return 0


def build_ikhtebar_report_html(
    data: Dict[str, Any], 
    working_days_list: List[date], 
    holidays_list: List[date]
) -> str:
    """
    Builds a premium, print-friendly assessment (Ikhtebar) report for all students.
    """
    from collections import defaultdict
    from datetime import datetime
    
    from_date = data.get("from_date", "")
    to_date = data.get("to_date", "")
    
    # Format date strings for display
    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        range_str = f"{from_dt.strftime('%d %B %Y')} - {to_dt.strftime('%d %B %Y')}"
    except Exception:
        range_str = f"{from_date} - {to_date}"
        
    students = data.get("students", [])
    jadeed_rows = data.get("jadeed", [])
    session_rows = data.get("sessions", [])
    jadeed_daily_rows = data.get("jadeed_daily", [])
    takhteet_rows = data.get("takhteet", [])
    
    # 1. Map student jadeed entries
    student_jadeed = defaultdict(list)
    for j in jadeed_rows:
        student_jadeed[j["student_id"]].append(j)
        
    # Sort each student's jadeed entries chronologically
    for s_id in student_jadeed:
        student_jadeed[s_id].sort(key=lambda x: (x.get("activity_date", ""), x.get("created_at", "")))
        
    # 2. Gather student presence dates
    student_activity_dates = defaultdict(set)
    
    for s in session_rows:
        student_activity_dates[s["student_id"]].add(str(s["activity_date"]))
        
    for jd in jadeed_daily_rows:
        student_activity_dates[jd["student_id"]].add(str(jd["activity_date"]))
        
    for t in takhteet_rows:
        if t.get("murajat_text_clean") or t.get("juzulhali_text_clean") or t.get("jadeed_text_clean"):
            student_activity_dates[t["student_id"]].add(str(t["activity_date"]))
            
    for j in jadeed_rows:
        student_activity_dates[j["student_id"]].add(str(j["activity_date"]))
        
    # 3. Gather student marks
    student_marks = defaultdict(list)
    for s in session_rows:
        if s.get("marks") is not None:
            student_marks[s["student_id"]].append(float(s["marks"]))
            
    total_working_days = len(working_days_list)
    
    # Build rows
    table_rows = []
    
    for idx, s in enumerate(students):
        s_id = s["id"]
        s_name = s["full_name"]
        
        # Jadeed Start / End
        s_jadeed = student_jadeed.get(s_id, [])
        if s_jadeed:
            in_range_entries = [j for j in s_jadeed if from_date <= j.get("activity_date", "") <= to_date]
            if in_range_entries:
                last_j = in_range_entries[-1]
                before_range_entries = [j for j in s_jadeed if j.get("activity_date", "") < from_date]
                if before_range_entries:
                    first_j = before_range_entries[-1]
                    is_start_before_range = True
                else:
                    first_j = in_range_entries[0]
                    is_start_before_range = False
                
                f_surah = first_j.get("surahs") or {}
                f_surah_num = int(f_surah.get("number", 0))
                f_surah_name = f_surah.get("name_en", "Unknown")
                f_ayah = int(first_j.get("ayah_number") or 1)
                
                l_surah = last_j.get("surahs") or {}
                l_surah_num = int(l_surah.get("number", 0))
                l_surah_name = l_surah.get("name_en", "Unknown")
                l_ayah = int(last_j.get("ayah_number") or 1)
                
                # Lookup Quran page numbers dynamically using metadata to override any database entry errors
                f_page = get_quran_page(f_surah_num, f_ayah) or first_j.get("page_number")
                l_page = get_quran_page(l_surah_num, l_ayah) or last_j.get("page_number")
                
                jadeed_start_str = f"{f_surah_num} - {f_surah_name} (Ayah {f_ayah})"
                jadeed_end_str = f"{l_surah_num} - {l_surah_name} (Ayah {l_ayah})"
                
                if f_page is not None and l_page is not None:
                    if is_start_before_range:
                        total_pages = abs(int(l_page) - int(f_page))
                    else:
                        total_pages = abs(int(l_page) - int(f_page)) + 1
                else:
                    total_pages = 0
            else:
                jadeed_start_str = "-"
                jadeed_end_str = "-"
                total_pages = 0
        else:
            jadeed_start_str = "-"
            jadeed_end_str = "-"
            total_pages = 0
            
        # Presence and Absence
        present_count = 0
        for wd in working_days_list:
            if wd.isoformat() in student_activity_dates[s_id]:
                present_count += 1
        absent_count = total_working_days - present_count
        
        present_str = f"{present_count} / {total_working_days}"
        absent_str = f"{absent_count} / {total_working_days}"
        
        # Grade Calculation based on total_pages completed
        if total_pages >= 3:
            grade_class = "grade-jayyid"
            grade_label = "Jayyid"
        elif total_pages > 0:
            grade_class = "grade-mutawassit"
            grade_label = "Mutawassit"
        else:
            grade_class = ""
            grade_label = ""
            
        if grade_label:
            grade_badge = f'<span class="grade-badge {grade_class}">{grade_label}</span>'
        else:
            grade_badge = '<span class="muted">-</span>'
            
        # Alternating row background
        row_bg_class = "even-row" if idx % 2 == 1 else "odd-row"
        
        table_rows.append(f"""
        <tr class="{row_bg_class}">
            <td style="font-weight: 600; color: #1b4d3e;">{escape(s_name)}</td>
            <td style="font-size: 8.5pt;">{escape(jadeed_start_str)}</td>
            <td style="font-size: 8.5pt;">{escape(jadeed_end_str)}</td>
            <td style="font-weight: 700; text-align: center;">{total_pages}</td>
            <td style="text-align: center; color: #1b4d3e; font-weight: 500;">{present_str}</td>
            <td style="text-align: center; color: #9b2c2c; font-weight: 500;">{absent_str}</td>
            <td style="text-align: center;">{grade_badge}</td>
        </tr>
        """)
        
    # Return full HTML
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>OPR - One Page Report</title>
  <style>
    :root {{
      --green-dark: #1b4d3e;
      --gold: #c5a880;
      --gray-light: #fcfbfa;
      --gray-border: #e8e4db;
      --text: #333333;
    }}
    body {{
      font-family: 'Outfit', 'Inter', 'Segoe UI', sans-serif;
      margin: 0;
      padding: 30px;
      color: var(--text);
      background-color: #ffffff;
    }}
    .header-banner {{
      background: linear-gradient(135deg, var(--green-dark) 0%, #113027 100%);
      padding: 25px 30px;
      border-radius: 12px;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      margin-bottom: 25px;
      border: 1px solid var(--gold);
    }}
    .header-title {{
      margin: 0;
      font-size: 20pt;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .header-subtitle {{
      margin: 0;
      font-size: 9.5pt;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: var(--gold);
      font-weight: 600;
    }}
    
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
      font-size: 9.5pt;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }}
    th {{
      background-color: var(--green-dark);
      color: white;
      padding: 12px 10px;
      font-weight: 600;
      font-size: 8.5pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border: 1px solid var(--green-dark);
    }}
    td {{
      padding: 10px;
      border: 1px solid var(--gray-border);
    }}
    .odd-row {{
      background-color: #ffffff;
    }}
    .even-row {{
      background-color: var(--gray-light);
    }}
    
    .grade-badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 8.5pt;
      font-weight: 600;
      text-align: center;
    }}
    .grade-jayyid {{
      background-color: rgba(27, 77, 62, 0.1);
      color: #1b4d3e;
      border: 1px solid rgba(27, 77, 62, 0.2);
    }}
    .grade-mutawassit {{
      background-color: rgba(197, 168, 128, 0.15);
      color: #b38f59;
      border: 1px solid rgba(197, 168, 128, 0.3);
    }}
    
    .muted {{
      color: #95a5a6;
    }}
    
    .print-btn {{
      position: fixed;
      bottom: 25px;
      right: 25px;
      background-color: var(--green-dark);
      color: white;
      border: 1px solid var(--gold);
      padding: 12px 24px;
      border-radius: 30px;
      font-size: 10pt;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(0,0,0,0.15);
      z-index: 1000;
      transition: all 0.2s ease;
    }}
    .print-btn:hover {{
      background-color: #113027;
      transform: translateY(-2px);
    }}
    
    @media print {{
      body {{
        padding: 0;
      }}
      .print-btn {{
        display: none !important;
      }}
      .header-banner {{
        box-shadow: none;
        border: 1px solid #000;
      }}
      table {{
        page-break-inside: auto;
      }}
      tr {{
        page-break-inside: avoid;
        page-break-after: auto;
      }}
      thead {{
        display: table-header-group;
      }}
    }}
  </style>
</head>
<body>

  <!-- Header Banner -->
  <div class="header-banner">
    <div>
      <div class="header-subtitle">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div class="header-title">OPR - One Page Report (تقرير الصفحة الواحدة)</div>
    </div>
    <div style="text-align: right;">
      <div class="header-subtitle">Date Range</div>
      <div style="font-size: 11pt; font-weight: bold; margin-top: 1px;">{escape(range_str)}</div>
    </div>
  </div>

  <!-- Report Data Grid Table -->
  <table>
    <thead>
      <tr>
        <th style="text-align: left; width: 22%;">Student Name</th>
        <th style="text-align: left; width: 22%;">Jadeed Start (First Entry)</th>
        <th style="text-align: left; width: 22%;">Jadeed End (Latest Entry)</th>
        <th style="width: 10%;">Total Pages</th>
        <th style="width: 12%;">Days Present</th>
        <th style="width: 12%;">Days Absent</th>
        <th style="width: 10%;">Grade</th>
      </tr>
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


def build_ummul_banin_report_html(report_data: List[Dict[str, Any]]) -> str:
    """
    Generates a beautiful HTML report containing the latest Jadeed recitation
    and complete Takhteet (Jadeed, Juzulhali, Murajat) for all students.
    """
    table_rows = []
    
    for idx, s in enumerate(report_data):
        s_name = s["student_name"]
        entry = s["entry"]
        is_historical = s["is_historical"]
        is_no_jadeed_today = s["is_no_jadeed_today"]
        takhteet_jadeed = s.get("takhteet_jadeed", "") or ""
        takhteet_juzulhali = s.get("takhteet_juzulhali", "") or ""
        takhteet_murajat = s.get("takhteet_murajat", "") or ""
        
        # Determine status and color badge
        if entry is None:
            status_badge = '<span class="status-badge status-none">No History</span>'
            date_str = "-"
            recitation_str = "No Jadeed entry found"
        else:
            activity_date = entry.get("activity_date") or ""
            # Format date for readability
            try:
                dt = datetime.strptime(str(activity_date), "%Y-%m-%d")
                date_str = dt.strftime("%b %d, %Y")
            except Exception:
                date_str = str(activity_date)
                
            surah = entry.get("surahs") or {}
            if isinstance(surah, list):
                surah = surah[0] if surah else {}
            surah_name = surah.get("name_en") or ""
            
            p_num = entry.get("page_number") or 0
            a_num = entry.get("ayah_number") or 0
            vol = entry.get("volume") or ""
            
            recitation_parts = []
            if surah_name:
                recitation_parts.append(surah_name)
            if p_num > 0:
                recitation_parts.append(f"Pg {p_num}")
            if a_num > 0:
                recitation_parts.append(f"Ayah {a_num}")
            if vol:
                recitation_parts.append(f"Vol {vol}")
                
            recitation_str = ", ".join(recitation_parts) if recitation_parts else "-"
            
            if is_no_jadeed_today:
                status_badge = '<span class="status-badge status-no-jadeed">No Jadeed (Today)</span>'
            elif is_historical:
                status_badge = '<span class="status-badge status-historical">Last Recited</span>'
            else:
                status_badge = '<span class="status-badge status-today">Today\'s Jadeed</span>'
                
        # Build multi-line Takhteet items with badges
        hw_items = []
        if takhteet_jadeed.strip():
            hw_items.append(f"""<div style="margin-bottom: 4px;"><span class="hw-pill hw-jadeed">Jadeed</span> <span style="color: #222; font-weight: 500; word-break: break-word;">{escape(takhteet_jadeed)}</span></div>""")
        if takhteet_juzulhali.strip():
            hw_items.append(f"""<div style="margin-bottom: 4px;"><span class="hw-pill hw-juzulhali">Juzulhali</span> <span style="color: #222; font-weight: 500; word-break: break-word;">{escape(takhteet_juzulhali)}</span></div>""")
        if takhteet_murajat.strip():
            hw_items.append(f"""<div><span class="hw-pill hw-murajat">Murajat</span> <span style="color: #222; font-weight: 500; word-break: break-word;">{escape(takhteet_murajat)}</span></div>""")
            
        if hw_items:
            takhteet_html = "".join(hw_items)
        else:
            takhteet_html = '<span class="muted">-</span>'

        # Alternating row background
        row_bg_class = "even-row" if idx % 2 == 1 else "odd-row"
        
        table_rows.append(f"""
        <tr class="{row_bg_class}">
            <td style="font-weight: 600; color: #1b4d3e; font-size: 9.5pt;">{escape(s_name)}</td>
            <td style="text-align: center; font-size: 9pt;">{status_badge}</td>
            <td style="font-size: 9.5pt; font-weight: 500;">{escape(recitation_str)}</td>
            <td style="text-align: center; font-size: 9pt; font-weight: 500; color: #666;">{escape(date_str)}</td>
            <td style="font-size: 9pt; font-family: sans-serif; line-height: 1.4; padding: 8px 10px;">{takhteet_html}</td>
        </tr>
        """)
        
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Ummul Banin Ben Report</title>
  <style>
    :root {{
      --green-dark: #1b4d3e;
      --gold: #c5a880;
      --gray-light: #fcfbfa;
      --gray-border: #e8e4db;
      --text: #333333;
    }}
    body {{
      font-family: 'Outfit', 'Inter', 'Segoe UI', sans-serif;
      margin: 0;
      padding: 30px;
      color: var(--text);
      background-color: #ffffff;
    }}
    .header-banner {{
      background: linear-gradient(135deg, var(--green-dark) 0%, #113027 100%);
      padding: 25px 30px;
      border-radius: 12px;
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      margin-bottom: 25px;
      border: 1px solid var(--gold);
    }}
    .header-title {{
      margin: 0;
      font-size: 20pt;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .header-subtitle {{
      margin: 0;
      font-size: 9.5pt;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: var(--gold);
      font-weight: 600;
    }}
    
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
      font-size: 9.5pt;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }}
    th {{
      background-color: var(--green-dark);
      color: white;
      padding: 12px 10px;
      font-weight: 600;
      font-size: 8.5pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border: 1px solid var(--green-dark);
    }}
    td {{
      padding: 10px;
      border: 1px solid var(--gray-border);
      vertical-align: middle;
    }}
    .odd-row {{
      background-color: #ffffff;
    }}
    .even-row {{
      background-color: var(--gray-light);
    }}
    
    .status-badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 8pt;
      font-weight: 600;
      text-align: center;
      width: 110px;
    }}
    .status-today {{
      background-color: #e2f0d9;
      color: #385723;
      border: 1px solid #c5e0b4;
    }}
    .status-no-jadeed {{
      background-color: #fce4d6;
      color: #c65911;
      border: 1px solid #f8cbad;
    }}
    .status-historical {{
      background-color: #fff2cc;
      color: #7f6000;
      border: 1px solid #ffe699;
    }}
    .status-none {{
      background-color: #f2f2f2;
      color: #7f7f7f;
      border: 1px solid #d9d9d9;
    }}
    .hw-pill {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 7.5pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      margin-right: 4px;
      vertical-align: middle;
    }}
    .hw-jadeed {{
      background-color: #e2f0d9;
      color: #276a3c;
      border: 1px solid #c5e0b4;
    }}
    .hw-juzulhali {{
      background-color: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }}
    .hw-murajat {{
      background-color: #ebf8ff;
      color: #2b6cb0;
      border: 1px solid #bee3f8;
    }}
    .muted {{
      color: #999;
      font-style: italic;
    }}
    .print-btn {{
      position: fixed;
      bottom: 25px;
      right: 25px;
      background: linear-gradient(135deg, var(--green-dark) 0%, #113027 100%);
      color: white;
      border: 1px solid var(--gold);
      padding: 12px 20px;
      border-radius: 50px;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(0,0,0,0.2);
      font-size: 10pt;
      transition: all 0.2s ease;
      font-family: inherit;
    }}
    .print-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }}
    
    @media print {{
      .print-btn {{
        display: none;
      }}
      body {{
        padding: 0;
        background-color: #ffffff;
      }}
    }}
  </style>
</head>
<body>

  <!-- Header Banner -->
  <div class="header-banner">
    <div>
      <div class="header-subtitle">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div class="header-title">Ummul Banin Ben Report (تقرير أم البنين)</div>
    </div>
    <div style="text-align: right;">
      <div class="header-subtitle">Report Date</div>
      <div style="font-size: 11pt; font-weight: bold; margin-top: 1px;">{datetime.now().strftime("%B %d, %Y")}</div>
    </div>
  </div>

  <!-- Report Data Grid Table -->
  <table>
    <thead>
      <tr>
        <th style="text-align: left; width: 17%;">Student Name</th>
        <th style="width: 13%;">Status</th>
        <th style="text-align: left; width: 22%;">Latest Jadeed Recited</th>
        <th style="width: 12%;">Recitation Date</th>
        <th style="text-align: left; width: 36%;">Takhteet (Homework)</th>
      </tr>
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


def _format_pages_num(val: float) -> str:
    if val <= 0:
        return "0"
    if float(val).is_integer():
        return str(int(val))
    return f"{val:.2f}".rstrip("0").rstrip(".")


def build_jadeed_pages_summary_html(data: Dict[str, Any]) -> str:
    """
    Builds a responsive, elegant HTML table and print view for Jadeed Total Pages by student,
    broken down by month and sorted in descending order.
    """
    from datetime import datetime
    
    from_date = data.get("from_date", "")
    to_date = data.get("to_date", "")
    months = data.get("months", [])
    students = data.get("students", [])
    stats = data.get("stats", {})

    try:
        f_dt = datetime.strptime(from_date, "%Y-%m-%d")
        t_dt = datetime.strptime(to_date, "%Y-%m-%d")
        range_label = f"{f_dt.strftime('%b %d, %Y')} — {t_dt.strftime('%b %d, %Y')}"
    except Exception:
        range_label = f"{from_date} — {to_date}"

    # Calculate monthly totals for the summary footer row
    month_totals = {m["key"]: 0.0 for m in months}
    for s in students:
        for m_key, pgs in s.get("months_pages", {}).items():
            month_totals[m_key] += pgs

    total_class_pages = stats.get("total_class_pages", 0.0)

    # Build Header Months Th
    month_th_list = []
    for m in months:
        month_th_list.append(f'<th style="text-align: center; width: {max(9, int(45 / max(len(months), 1)))}%;">{escape(m["short_label"])}</th>')
    month_ths = "".join(month_th_list)

    # Build Table Rows
    table_rows = []
    for s in students:
        has_jadeed = s.get("has_jadeed", False)
        tot_pages = s.get("total_pages", 0.0)
        rank_val = s.get("rank", "-")
        s_name = s.get("student_name", "")
        
        # Monthly Cells
        month_cells = []
        for m in months:
            m_val = s.get("months_pages", {}).get(m["key"], 0.0)
            if m_val > 0:
                month_cells.append(f'<td class="page-col" style="text-align: center; font-weight: 600; color: #166534;"><span class="month-pill">{_format_pages_num(m_val)}</span></td>')
            else:
                month_cells.append('<td class="page-col" style="text-align: center; color: #9ca3af; font-size: 8.5pt;">-</td>')
        
        month_cells_str = "".join(month_cells)

        if has_jadeed and tot_pages > 0:
            rank_badge = f'<span class="rank-badge rank-active">{rank_val}</span>'
            if rank_val == 1:
                rank_badge = '<span class="rank-badge rank-gold">🥇 1</span>'
            elif rank_val == 2:
                rank_badge = '<span class="rank-badge rank-silver">🥈 2</span>'
            elif rank_val == 3:
                rank_badge = '<span class="rank-badge rank-bronze">🥉 3</span>'

            tot_badge = f'<span class="tot-badge tot-active">{_format_pages_num(tot_pages)} pgs</span>'
            
            # Status milestone
            latest = s.get("latest_entry")
            if latest and latest.get("surah_name"):
                status_html = f'<div style="font-size: 8pt; color: #4b5563;">Surah {latest.get("surah_number")} ({latest.get("surah_name")}) p.{latest.get("page_number") or "-"}</div>'
            else:
                status_html = f'<span style="color: #166534; font-size: 8pt; font-weight: 500;">Active ({s.get("active_days", 0)} days)</span>'

            row_class = "student-row-active"
        else:
            rank_badge = '<span class="rank-badge rank-none">-</span>'
            tot_badge = '<span class="tot-badge tot-zero">0 pgs</span>'
            status_html = '<span class="badge-no-jadeed">No Jadeed Recorded</span>'
            row_class = "student-row-empty"

        table_rows.append(f"""
        <tr class="{row_class}">
          <td style="text-align: center; width: 6%;">{rank_badge}</td>
          <td style="font-weight: 600; color: #111827; text-align: left;">{escape(s_name)}</td>
          {month_cells_str}
          <td style="text-align: center; width: 14%;">{tot_badge}</td>
          <td style="text-align: left; width: 22%;">{status_html}</td>
        </tr>
        """)

    # Footer Row
    month_footers = []
    for m in months:
        m_tot = month_totals.get(m["key"], 0.0)
        month_footers.append(f'<td style="text-align: center; font-weight: 700; color: #065f46;">{_format_pages_num(m_tot)}</td>')
    month_footers_str = "".join(month_footers)

    footer_row = f"""
    <tr class="footer-summary-row">
      <td colspan="2" style="text-align: right; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding-right: 15px;">Class Monthly Totals:</td>
      {month_footers_str}
      <td style="text-align: center; font-weight: 800; color: #064e3b; font-size: 10pt;">{_format_pages_num(total_class_pages)} pgs</td>
      <td style="font-size: 8.5pt; font-weight: 600; color: #4b5563;">{stats.get('students_with_jadeed', 0)} of {stats.get('total_students', 0)} Students Active</td>
    </tr>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Jadeed Total Pages Summary — {range_label}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>

    :root {{
      --emerald-dark: #074332;
      --emerald: #0E6B50;
      --emerald-light: #e6f4ea;
      --gold: #D4AF37;
      --gold-light: #fef9e7;
      --gold-dark: #b88917;
      --border-color: #e5e7eb;
      --bg-cream: #fbf9f5;
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f8fafc;
      color: #1f2937;
      font-size: 9pt;
      line-height: 1.4;
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      background-color: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
    }}

    /* Header Banner */
    .header-banner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, #074332 0%, #0E6B50 100%);
      color: #ffffff;
      padding: 20px 24px;
      border-radius: 10px;
      border: 1.5px solid var(--gold);
      margin-bottom: 20px;
      box-shadow: 0 4px 12px rgba(7, 67, 50, 0.15);
    }}

    .header-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 16pt;
      font-weight: 700;
      letter-spacing: 0.3px;
      color: #ffffff;
      margin: 0;
    }}

    .header-subtitle {{
      font-size: 8.5pt;
      color: var(--gold);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 3px;
    }}

    .date-badge {{
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(212, 175, 55, 0.5);
      color: #ffffff;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 8.5pt;
      font-weight: 600;
      text-align: right;
    }}

    /* KPI Summary Stats */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 22px;
    }}

    .kpi-card {{
      background-color: var(--bg-cream);
      border: 1px solid #e7e3da;
      border-radius: 8px;
      padding: 12px 14px;
      text-align: center;
    }}

    .kpi-label {{
      font-size: 7.5pt;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: #6b7280;
      font-weight: 600;
      margin-bottom: 4px;
    }}

    .kpi-val {{
      font-family: 'Outfit', sans-serif;
      font-size: 15pt;
      font-weight: 700;
      color: var(--emerald-dark);
    }}

    /* Main Table */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 9pt;
    }}

    th {{
      background-color: #f1f5f9;
      color: #374151;
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 10px 8px;
      border-top: 1.5px solid var(--border-color);
      border-bottom: 2px solid var(--border-color);
    }}

    td {{
      padding: 8px 8px;
      border-bottom: 1px solid #f1f5f9;
      vertical-align: middle;
    }}

    tr.student-row-active:hover {{
      background-color: #f8fafc;
    }}

    tr.student-row-empty {{
      background-color: #fafafa;
      opacity: 0.65;
    }}

    .rank-badge {{
      display: inline-block;
      min-width: 24px;
      padding: 2px 6px;
      border-radius: 12px;
      font-size: 7.5pt;
      font-weight: 700;
      text-align: center;
    }}

    .rank-gold {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
    .rank-silver {{ background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }}
    .rank-bronze {{ background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }}
    .rank-active {{ background: #e0f2fe; color: #0369a1; }}
    .rank-none {{ color: #9ca3af; }}

    .month-pill {{
      background-color: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 8.5pt;
    }}

    .tot-badge {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 14px;
      font-weight: 700;
      font-size: 9pt;
      font-family: 'Outfit', sans-serif;
    }}

    .tot-active {{
      background: linear-gradient(135deg, #074332 0%, #0E6B50 100%);
      color: #ffffff;
      border: 1px solid var(--gold);
      box-shadow: 0 2px 4px rgba(7, 67, 50, 0.15);
    }}

    .tot-zero {{
      background: #f3f4f6;
      color: #9ca3af;
      border: 1px solid #e5e7eb;
    }}

    .badge-no-jadeed {{
      background-color: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 7.5pt;
      font-weight: 600;
      display: inline-block;
    }}

    .footer-summary-row {{
      background-color: #f0fdf4 !important;
      border-top: 2px solid #86efac !important;
      border-bottom: 2px solid #86efac !important;
    }}

    .footer-summary-row td {{
      padding: 11px 8px;
    }}

    /* Print Button */
    .print-btn {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: linear-gradient(135deg, #074332, #0E6B50);
      color: #ffffff;
      border: 1.5px solid var(--gold);
      padding: 10px 18px;
      border-radius: 24px;
      font-weight: 700;
      font-size: 9.5pt;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      transition: all 0.2s ease;
      z-index: 9999;
    }}

    .print-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
      border-color: #ffffff;
    }}

    @media print {{
      body {{
        padding: 0;
        background-color: #ffffff;
      }}
      .container {{
        border: none;
        box-shadow: none;
        padding: 0;
        max-width: 100%;
      }}
      .print-btn {{
        display: none !important;
      }}
    }}
  </style>
</head>
<body>

  <div class="container">
    <!-- Header Banner -->
    <div class="header-banner">
      <div>
        <div class="header-subtitle">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
        <h1 class="header-title">تقرير مجموع صفحات الجديد للطلاب (Jadeed Pages Summary)</h1>
      </div>
      <div class="date-badge">
        <div style="font-size: 7.5pt; opacity: 0.8; text-transform: uppercase;">Selected Range</div>
        <div style="font-size: 9pt; font-weight: bold; margin-top: 1px;">{range_label}</div>
      </div>
    </div>

    <!-- Executive Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Class Pages</div>
        <div class="kpi-val" style="color: var(--emerald);">{_format_pages_num(total_class_pages)} <span style="font-size: 9pt; font-weight: normal; color: #6b7280;">pgs</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Active Jadeed Students</div>
        <div class="kpi-val">{stats.get('students_with_jadeed', 0)} <span style="font-size: 9pt; font-weight: normal; color: #6b7280;">/ {stats.get('total_students', 0)}</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Class Average</div>
        <div class="kpi-val">{stats.get('avg_pages_per_student', 0)} <span style="font-size: 9pt; font-weight: normal; color: #6b7280;">pgs/student</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🏆 Top Performer</div>
        <div class="kpi-val" style="font-size: 11pt; color: #92400e; margin-top: 4px;">{escape(stats.get('top_student', 'None'))}</div>
      </div>
    </div>

    <!-- Main Table Grid -->
    <table>
      <thead>
        <tr>
          <th style="width: 6%; text-align: center;">Rank</th>
          <th style="text-align: left;">Student Name</th>
          {month_ths}
          <th style="text-align: center; width: 14%;">Total Pages</th>
          <th style="text-align: left; width: 22%;">Status / Notes</th>
        </tr>
      </thead>
      <tbody>
        {"".join(table_rows)}
      </tbody>
      <tfoot>
        {footer_row}
      </tfoot>
    </table>
  </div>

  <!-- Print Button -->
  <button class="print-btn" onclick="window.print()">🖨️ Print / Save PDF</button>

</body>
</html>
"""


def build_unified_3in1_report_html(student_name: str, rows: List[Dict[str, Any]]) -> str:
    """
    Builds a unified 3-in-1 monthly recitation summary report containing:
    - Murajat: Surah, Page No, Marks
    - Juzulhali: Surah, Page No, Marks
    - Jadeed: Surah, Page No, Ayah No (No Volume)
    """
    sorted_rows = sorted(rows, key=lambda x: x.get("activity_date", ""))
    month_year_str = _get_month_year_str(sorted_rows)

    # Statistics Calculation
    total_active_days = 0
    total_working_days = 0
    murajat_pages = 0
    murajat_marks_sum = 0.0
    murajat_marks_count = 0
    juzulhali_pages = 0
    juzulhali_marks_sum = 0.0
    juzulhali_marks_count = 0
    jadeed_count = 0

    today_str = date.today().isoformat()

    for r in sorted_rows:
        activity_date = r.get("activity_date", "")
        try:
            dt = datetime.strptime(activity_date, "%Y-%m-%d")
            wd = dt.weekday()
        except Exception:
            wd = 0
        is_weekend = wd in (5, 6)

        if not is_weekend and activity_date <= today_str:
            total_working_days += 1

        murajat = r.get("murajat", [])
        juzulhali = r.get("juzulhali", [])
        jadeed = r.get("jadeed", [])
        t_m, t_j, t_jd = _get_takhteet_values(r.get("takhteet"))

        has_activity = bool(
            murajat or juzulhali or jadeed or not (
                r.get("no_jadeed", True)
                and not t_m.strip()
                and not t_j.strip()
                and not t_jd.strip()
            )
        )
        if has_activity and not is_weekend:
            total_active_days += 1

        # Murajat stats
        for m in murajat:
            murajat_pages += 1
            if "marks" in m:
                murajat_marks_sum += float(m.get("marks", 10.0))
                murajat_marks_count += 1

        # Juzulhali stats
        for j in juzulhali:
            juzulhali_pages += 1
            if "marks" in j:
                juzulhali_marks_sum += float(j.get("marks", 10.0))
                juzulhali_marks_count += 1

        # Jadeed stats
        if jadeed:
            jadeed_count += len(jadeed)

    avg_murajat_marks = (murajat_marks_sum / murajat_marks_count) if murajat_marks_count > 0 else 10.0
    avg_juzulhali_marks = (juzulhali_marks_sum / juzulhali_marks_count) if juzulhali_marks_count > 0 else 10.0

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
        t_m, t_j, t_jd = _get_takhteet_values(r.get("takhteet"))

        is_absent = (
            not is_weekend
            and activity_date <= today_str
            and not murajat
            and not juzulhali
            and not jadeed
            and not r.get("no_jadeed")
            and not t_m.strip()
            and not t_j.strip()
            and not t_jd.strip()
        )

        is_weekend_empty = (
            is_weekend
            and not murajat
            and not juzulhali
            and not jadeed
            and not r.get("no_jadeed")
            and not t_m.strip()
            and not t_j.strip()
            and not t_jd.strip()
        )

        # 1. Render Absent Row
        if is_absent:
            cells = [
                f'<td class="date-col"><div class="day-title">Day {date_num}</div><div class="day-subtitle">{day_name_en} {date_sub}</div></td>',
                '<td colspan="9" class="absent-cell" style="text-align: center; color: #b91c1c; font-style: italic; font-weight: 600; background-color: #fef2f2; padding: 8px;">Absent / غائب</td>'
            ]
            row_class = ' class="day-separator week-end-separator"' if wd == 6 else ' class="day-separator"'
            table_rows.append(f'<tr{row_class}>{"".join(cells)}</tr>')
            continue

        # 2. Render Empty Weekend Row
        if is_weekend_empty:
            weekend_label = "Saturday - Weekend" if wd == 5 else "Sunday - Weekend"
            cells = [
                f'<td class="date-col"><div class="day-title">Day {date_num}</div><div class="day-subtitle">{day_name_en} {date_sub}</div></td>',
                f'<td colspan="9" class="weekend-cell" style="text-align: center; color: #6b7280; background-color: #f8fafc; font-style: italic; padding: 8px;">{weekend_label}</td>'
            ]
            row_class = ' class="day-separator week-end-separator"' if wd == 6 else ' class="day-separator"'
            table_rows.append(f'<tr{row_class}>{"".join(cells)}</tr>')
            continue

        # 3. Active Day Rows
        N_rows = max(len(murajat), len(juzulhali), len(jadeed), 1)
        for sub_idx in range(N_rows):
            cells = []
            if sub_idx == 0:
                cells.append(
                    f'<td class="date-col" rowspan="{N_rows}">'
                    f'  <div class="day-title">Day {date_num}</div>'
                    f'  <div class="day-subtitle">{day_name_en} {date_sub}</div>'
                    f'</td>'
                )

            # Murajat Columns: Surah, Page, Marks + Duration
            if sub_idx < len(murajat):
                m = murajat[sub_idx]
                s_name = m.get("surah_name_ar") or m.get("surat") or ""
                if s_name and " - " in s_name:
                    parts = s_name.split(" - ")
                    s_name = parts[1] if len(parts) > 1 else s_name
                if not s_name and m.get("surahs"):
                    s_name = m["surahs"].get("name_en") or m["surahs"].get("name_ar") or ""

                p_val = m.get("page_number") or "-"
                try:
                    p_num = int(p_val)
                except (ValueError, TypeError):
                    p_num = 0
                surah_id = m.get("surah_id")
                if p_num in range(1, 31) and (surah_id == SIPARA_TO_SURAH.get(p_num) or not s_name or s_name == "Surah"):
                    s_name = SIPARA_NAMES.get(p_num, f"Sipara {p_num}")
                    p_val = "-"

                m_marks = m.get("marks", 10.0)
                grade_html = _format_grade_badge(m_marks)

                dur_sec = m.get("duration_seconds", 0)
                dur_badge = ""
                if dur_sec and int(dur_sec) > 0:
                    dur_m = int(dur_sec) // 60
                    dur_s = int(dur_sec) % 60
                    is_over = bool(m.get("time_exceeded") or int(dur_sec) > 600)
                    bg = "#fee2e2" if is_over else "#f0fdf4"
                    fg = "#dc2626" if is_over else "#0369a1"
                    dur_badge = f'<div style="font-size: 7pt; font-weight: bold; color: {fg}; background: {bg}; border-radius: 4px; padding: 1px 4px; margin-top: 2px;">⏱️ {dur_m}m {dur_s:02d}s{" (Over)" if is_over else ""}</div>'
                elif m.get("time_exceeded"):
                    dur_badge = '<div style="font-size: 7pt; font-weight: bold; color: #dc2626; background: #fee2e2; border-radius: 4px; padding: 1px 4px; margin-top: 2px;">⏱️ Overtime</div>'

                cells.append(f'<td class="text-left border-left-murajat" style="font-weight: 600; font-size: 8.5pt;">{escape(str(s_name))}</td>')
                cells.append(f'<td style="text-align: center; font-weight: 500;">{p_val}</td>')
                cells.append(f'<td style="text-align: center;">{grade_html}{dur_badge}</td>')
            elif len(murajat) == 0 and sub_idx == 0:
                cells.append('<td class="border-left-murajat" style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
                cells.append('<td style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
                cells.append('<td style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
            else:
                cells.append('<td class="border-left-murajat"></td><td></td><td></td>')

            # Juzulhali Columns: Surah, Page, Marks + Duration
            if sub_idx < len(juzulhali):
                j = juzulhali[sub_idx]
                s_name = j.get("surah_name_ar") or j.get("surat") or ""
                if s_name and " - " in s_name:
                    parts = s_name.split(" - ")
                    s_name = parts[1] if len(parts) > 1 else s_name
                if not s_name and j.get("surahs"):
                    s_name = j["surahs"].get("name_en") or j["surahs"].get("name_ar") or ""

                p_val = j.get("page_number") or "-"
                try:
                    p_num = int(p_val)
                except (ValueError, TypeError):
                    p_num = 0
                surah_id = j.get("surah_id")
                if surah_id and p_num in range(1, 31) and surah_id == SIPARA_TO_SURAH.get(p_num):
                    s_name = SIPARA_NAMES.get(p_num, f"Sipara {p_num}")
                    p_val = "-"
                elif not s_name:
                    s_name = "Juz'ul Hali"

                j_marks = j.get("marks", 10.0)
                grade_html = _format_grade_badge(j_marks)

                dur_sec = j.get("duration_seconds", 0)
                dur_badge = ""
                if dur_sec and int(dur_sec) > 0:
                    dur_m = int(dur_sec) // 60
                    dur_s = int(dur_sec) % 60
                    is_over = bool(j.get("time_exceeded") or int(dur_sec) > 900)
                    bg = "#fee2e2" if is_over else "#fef3c7"
                    fg = "#dc2626" if is_over else "#b45309"
                    dur_badge = f'<div style="font-size: 7pt; font-weight: bold; color: {fg}; background: {bg}; border-radius: 4px; padding: 1px 4px; margin-top: 2px;">⏱️ {dur_m}m {dur_s:02d}s{" (Over)" if is_over else ""}</div>'
                elif j.get("time_exceeded"):
                    dur_badge = '<div style="font-size: 7pt; font-weight: bold; color: #dc2626; background: #fee2e2; border-radius: 4px; padding: 1px 4px; margin-top: 2px;">⏱️ Overtime</div>'

                cells.append(f'<td class="text-left border-left-juzulhali" style="font-weight: 600; font-size: 8.5pt;">{escape(str(s_name))}</td>')
                cells.append(f'<td style="text-align: center; font-weight: 500;">{p_val}</td>')
                cells.append(f'<td style="text-align: center;">{grade_html}{dur_badge}</td>')
            elif len(juzulhali) == 0 and sub_idx == 0:
                cells.append('<td class="border-left-juzulhali" style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
                cells.append('<td style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
                cells.append('<td style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
            else:
                cells.append('<td class="border-left-juzulhali"></td><td></td><td></td>')

            # Jadeed Columns: Surah, Page, Ayah + Duration (NO VOLUME)
            if sub_idx < len(jadeed):
                jd = jadeed[sub_idx]
                s_name = jd.get("surah_name_ar") or jd.get("surat") or ""
                if s_name and " - " in s_name:
                    parts = s_name.split(" - ")
                    s_name = parts[1] if len(parts) > 1 else s_name
                if not s_name and jd.get("surahs"):
                    s_name = jd["surahs"].get("name_en") or jd["surahs"].get("name_ar") or ""

                p_val = jd.get("page_number") or "-"
                a_val = jd.get("ayah_number") or "-"

                dur_sec = jd.get("duration_seconds", 0)
                dur_badge = ""
                if dur_sec and int(dur_sec) > 0:
                    dur_m = int(dur_sec) // 60
                    dur_s = int(dur_sec) % 60
                    is_over = bool(jd.get("time_exceeded") or int(dur_sec) > 300)
                    bg = "#fee2e2" if is_over else "#f0fdf4"
                    fg = "#dc2626" if is_over else "#16a34a"
                    dur_badge = f'<div style="font-size: 7pt; font-weight: bold; color: {fg}; background: {bg}; border-radius: 4px; padding: 1px 4px; margin-top: 2px;">⏱️ {dur_m}m {dur_s:02d}s{" (Over)" if is_over else ""}</div>'
                elif jd.get("time_exceeded"):
                    dur_badge = '<div style="font-size: 7pt; font-weight: bold; color: #dc2626; background: #fee2e2; border-radius: 4px; padding: 1px 4px; margin-top: 2px;">⏱️ Overtime</div>'

                jd_flags = []
                if jd.get("weak_hifz"):
                    jd_flags.append("Weak Hifz")
                if jd.get("airab_mistakes"):
                    jd_flags.append("Airab")
                if jd.get("weak_murajat"):
                    jd_flags.append("Weak Mur")
                if jd.get("weak_juzulhali"):
                    jd_flags.append("Weak JH")

                flag_spans = ""
                if jd_flags:
                    flag_spans = '<div style="margin-top: 2px;">' + " ".join([f'<span style="display:inline-block; font-size:6.5pt; font-weight:600; color:#c2410c; background:#fff7ed; border:1px solid #ffedd5; border-radius:3px; padding:0 3px;">{escape(f)}</span>' for f in jd_flags]) + '</div>'

                cells.append(f'<td class="text-left border-left-jadeed" style="font-weight: 600; font-size: 8.5pt;">{escape(str(s_name))}{flag_spans}</td>')
                cells.append(f'<td style="text-align: center; font-weight: 500;">{p_val}</td>')
                cells.append(f'<td style="text-align: center; font-weight: 500;">{a_val}{dur_badge}</td>')
            elif r.get("no_jadeed") and sub_idx == 0:
                reasons = r.get("no_jadeed_reasons") or []
                if not reasons and r.get("no_jadeed_details"):
                    jd_det = r.get("no_jadeed_details")
                    if jd_det.get("weak_hifz"): reasons.append("Weak Hifz")
                    if jd_det.get("airab_mistakes"): reasons.append("Airab Mistakes")
                    if jd_det.get("time_exceeded"): reasons.append("Time Exceeded")
                    if jd_det.get("weak_murajat"): reasons.append("Weak Murajat")
                    if jd_det.get("weak_juzulhali"): reasons.append("Weak Juz'ul Hali")
                if reasons:
                    badge_spans = " ".join([f'<span style="display:inline-block; font-size:7pt; font-weight:600; color:#9a3412; background:#ffedd5; border:1px solid #fed7aa; border-radius:3px; padding:1px 4px; margin:1px;">{escape(rs)}</span>' for rs in reasons])
                    cells.append(f'<td colspan="3" class="border-left-jadeed" style="text-align: center; color: #854d0e; background: #fef9c3; font-size: 8pt; padding: 3px;"><div><em>No Jadeed</em></div><div style="margin-top:2px;">{badge_spans}</div></td>')
                else:
                    cells.append('<td colspan="3" class="border-left-jadeed" style="text-align: center; color: #854d0e; background: #fef9c3; font-style: italic; font-size: 8pt; padding: 4px;">No Jadeed</td>')
            elif len(jadeed) == 0 and sub_idx == 0:
                cells.append('<td class="border-left-jadeed" style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
                cells.append('<td style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
                cells.append('<td style="text-align: center; color: #9ca3af; font-size: 8pt;">-</td>')
            else:
                cells.append('<td class="border-left-jadeed"></td><td></td><td></td>')

            is_last_sub = (sub_idx == N_rows - 1)
            row_class = ' class="day-separator week-end-separator"' if (is_last_sub and wd == 6) else (' class="day-separator"' if is_last_sub else '')
            table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")

    attendance_pct = (total_active_days / total_working_days * 100) if total_working_days > 0 else 100.0

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Unified Recitation Summary — {escape(student_name)} ({month_year_str})</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --emerald-dark: #074332;
      --emerald: #0E6B50;
      --gold: #D4AF37;
      --gold-dark: #b88917;
      --murajat-color: #0369a1;
      --murajat-bg: #e0f2fe;
      --juzulhali-color: #b45309;
      --juzulhali-bg: #fef3c7;
      --jadeed-color: #15803d;
      --jadeed-bg: #dcfce7;
      --border-color: #e5e7eb;
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 16px;
      background-color: #f8fafc;
      color: #1f2937;
      font-size: 8.5pt;
      line-height: 1.35;
    }}

    .container {{
      max-width: 1150px;
      margin: 0 auto;
      background-color: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
    }}

    /* Header Banner */
    .header-banner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, #074332 0%, #0E6B50 100%);
      color: #ffffff;
      padding: 16px 20px;
      border-radius: 10px;
      border: 1.5px solid var(--gold);
      margin-bottom: 16px;
    }}

    .header-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 15pt;
      font-weight: 700;
      color: #ffffff;
      margin: 0;
    }}

    .header-subtitle {{
      font-size: 8pt;
      color: var(--gold);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 2px;
    }}

    .student-badge {{
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(212, 175, 55, 0.5);
      color: #ffffff;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 8.5pt;
      font-weight: 600;
      text-align: right;
    }}

    /* KPI Summary Stats */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-bottom: 16px;
    }}

    .kpi-card {{
      border-radius: 8px;
      padding: 10px 12px;
      text-align: center;
      border: 1px solid var(--border-color);
    }}

    .kpi-card-murajat {{ background-color: #f0f9ff; border-color: #bae6fd; }}
    .kpi-card-juzulhali {{ background-color: #fffbeb; border-color: #fde68a; }}
    .kpi-card-jadeed {{ background-color: #f0fdf4; border-color: #bbf7d0; }}
    .kpi-card-att {{ background-color: #fbf9f5; border-color: #e7e3da; }}

    .kpi-label {{
      font-size: 7pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 700;
      margin-bottom: 3px;
    }}

    .kpi-val {{
      font-family: 'Outfit', sans-serif;
      font-size: 13pt;
      font-weight: 700;
    }}

    /* Main Table */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 8.5pt;
    }}

    th {{
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      padding: 7px 6px;
      border: 1px solid var(--border-color);
      text-align: center;
    }}

    td {{
      padding: 6px 6px;
      border: 1px solid #f1f5f9;
      vertical-align: middle;
    }}

    .text-left {{ text-align: left !important; }}

    .date-col {{
      width: 11%;
      background-color: #f8fafc;
      text-align: center;
      font-weight: 600;
      border-right: 1.5px solid #cbd5e1 !important;
    }}

    .day-title {{
      font-weight: 700;
      color: #1e293b;
      font-size: 8.5pt;
    }}

    .day-subtitle {{
      font-size: 7pt;
      color: #64748b;
    }}

    .border-left-murajat {{ border-left: 2px solid #38bdf8 !important; }}
    .border-left-juzulhali {{ border-left: 2px solid #f59e0b !important; }}
    .border-left-jadeed {{ border-left: 2px solid #22c55e !important; }}

    .grade-badge {{
      display: inline-block;
      padding: 1px 6px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 7.5pt;
    }}

    .grade-excellent {{ background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }}
    .grade-passing {{ background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
    .grade-warning {{ background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}

    tr.day-separator td {{
      border-bottom: 1.5px solid #cbd5e1;
    }}

    tr.week-end-separator td {{
      border-bottom: 2.5px solid #94a3b8;
    }}

    /* Print Button */
    .print-btn {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: linear-gradient(135deg, #074332, #0E6B50);
      color: #ffffff;
      border: 1.5px solid var(--gold);
      padding: 9px 16px;
      border-radius: 20px;
      font-weight: 700;
      font-size: 9pt;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      transition: all 0.2s ease;
      z-index: 9999;
    }}

    .print-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
      border-color: #ffffff;
    }}

    @media print {{
      body {{
        padding: 0;
        background-color: #ffffff;
      }}
      .container {{
        border: none;
        box-shadow: none;
        padding: 0;
        max-width: 100%;
      }}
      .print-btn {{
        display: none !important;
      }}
    }}
  </style>
</head>
<body>

  <div class="container">
    <!-- Header Banner -->
    <div class="header-banner">
      <div>
        <div class="header-subtitle">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
        <h1 class="header-title">Monthly Recitation Summary (تقرير التسميع الشهري الشامل)</h1>
      </div>
      <div class="student-badge">
        <div style="font-size: 7.5pt; opacity: 0.8; text-transform: uppercase;">Student / Month</div>
        <div style="font-size: 9.5pt; font-weight: bold; margin-top: 1px;">{escape(student_name)} • {month_year_str}</div>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-murajat">
        <div class="kpi-label" style="color: var(--murajat-color);">👥 Murajat Pages / Avg</div>
        <div class="kpi-val" style="color: var(--murajat-color);">{murajat_pages} <span style="font-size: 8.5pt; font-weight: normal; color: #475569;">pgs • Avg {avg_murajat_marks:.1f}/10</span></div>
      </div>
      <div class="kpi-card kpi-card-juzulhali">
        <div class="kpi-label" style="color: var(--juzulhali-color);">📖 Juzulhali Pages / Avg</div>
        <div class="kpi-val" style="color: var(--juzulhali-color);">{juzulhali_pages} <span style="font-size: 8.5pt; font-weight: normal; color: #475569;">pgs • Avg {avg_juzulhali_marks:.1f}/10</span></div>
      </div>
      <div class="kpi-card kpi-card-jadeed">
        <div class="kpi-label" style="color: var(--jadeed-color);">📝 Jadeed Lessons</div>
        <div class="kpi-val" style="color: var(--jadeed-color);">{jadeed_count} <span style="font-size: 8.5pt; font-weight: normal; color: #475569;">recitations</span></div>
      </div>
      <div class="kpi-card kpi-card-att">
        <div class="kpi-label" style="color: #4b5563;">📅 Attendance</div>
        <div class="kpi-val" style="color: var(--emerald-dark);">{total_active_days} / {total_working_days} <span style="font-size: 8.5pt; font-weight: normal; color: #6b7280;">({attendance_pct:.0f}%)</span></div>
      </div>
    </div>

    <!-- Main Table Grid -->
    <table>
      <thead>
        <tr>
          <th rowspan="2" style="width: 11%; background-color: #f1f5f9;">Date</th>
          <th colspan="3" style="background: var(--murajat-bg); color: var(--murajat-color); border-bottom: 2px solid #38bdf8;">👥 Murajat (مراجعة)</th>
          <th colspan="3" style="background: var(--juzulhali-bg); color: var(--juzulhali-color); border-bottom: 2px solid #f59e0b;">📖 Juzulhali (جزء الحالي)</th>
          <th colspan="3" style="background: var(--jadeed-bg); color: var(--jadeed-color); border-bottom: 2px solid #22c55e;">📝 Jadeed (جديد)</th>
        </tr>
        <tr>
          <!-- Murajat -->
          <th style="background: #f0f9ff; color: var(--murajat-color); width: 17%;">Sipara / Surah</th>
          <th style="background: #f0f9ff; color: var(--murajat-color); width: 6%;">Page</th>
          <th style="background: #f0f9ff; color: var(--murajat-color); width: 7%;">Marks</th>
          <!-- Juzulhali -->
          <th style="background: #fffbeb; color: var(--juzulhali-color); width: 17%;">Sipara / Surah</th>
          <th style="background: #fffbeb; color: var(--juzulhali-color); width: 6%;">Page</th>
          <th style="background: #fffbeb; color: var(--juzulhali-color); width: 7%;">Marks</th>
          <!-- Jadeed -->
          <th style="background: #f0fdf4; color: var(--jadeed-color); width: 17%;">Surah</th>
          <th style="background: #f0fdf4; color: var(--jadeed-color); width: 6%;">Page</th>
          <th style="background: #f0fdf4; color: var(--jadeed-color); width: 6%;">Ayah</th>
        </tr>
      </thead>
      <tbody>
        {"".join(table_rows)}
      </tbody>
    </table>
  </div>

  <!-- Print Button -->
  <button class="print-btn" onclick="window.print()">🖨️ Print / Save PDF</button>

</body>
</html>
"""


def build_teacher_detailed_attendance_html(
    *,
    teacher_name: str,
    teacher_username: str = "",
    from_date: str,
    to_date: str,
    records: List[Dict[str, Any]],
) -> str:
    """
    Generates a high-fidelity, A4 printable day-wise attendance report HTML for a teacher,
    including Sundays, status, and login times.
    """
    from html import escape
    from datetime import datetime

    total_days = len(records)
    present_days = sum(1 for r in records if r.get("is_present"))
    absent_days = total_days - present_days
    pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0

    # Format Date Range string
    try:
        f_dt = datetime.strptime(from_date, "%Y-%m-%d").strftime("%d %b %Y")
        t_dt = datetime.strptime(to_date, "%Y-%m-%d").strftime("%d %b %Y")
        range_str = f"{f_dt} to {t_dt}" if f_dt != t_dt else f_dt
    except Exception:
        range_str = f"{from_date} to {to_date}"

    rows_html = []
    for idx, r in enumerate(records, 1):
        day_name = r.get("day_name", "")
        f_date = r.get("formatted_date") or r.get("date", "")
        is_sun = r.get("is_sunday", False)
        is_pres = r.get("is_present", False)
        login_time = r.get("login_time", "-")

        # Row style for Sundays
        row_style = ' style="background-color: #fdfaf0;"' if is_sun else ""
        sun_badge = ' <span class="badge-sunday">Sunday</span>' if is_sun else ""

        if is_pres:
            status_html = '<span class="badge-present">🟢 Present</span>'
            time_html = f'<span class="time-present">{escape(login_time)}</span>'
        else:
            status_html = '<span class="badge-absent">🔴 Absent</span>'
            time_html = '<span class="time-absent">-</span>'

        rows_html.append(f"""
        <tr{row_style}>
          <td style="text-align: center; color: #718096; font-weight: 500;">{idx}</td>
          <td style="font-weight: 600; color: #2d3748;">{escape(day_name)}{sun_badge}</td>
          <td style="font-weight: 500; color: #4a5568;">{escape(f_date)}</td>
          <td style="text-align: center;">{status_html}</td>
          <td style="text-align: center; font-weight: 600;">{time_html}</td>
        </tr>
        """)

    table_rows_str = "\n".join(rows_html)
    username_sub = f" <span style='font-size: 11pt; font-weight: normal; color: #718096;'>({escape(teacher_username)})</span>" if teacher_username else ""

    return f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8"/>
  <title>Teacher Attendance Report - {escape(teacher_name)}</title>
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
    .print-btn {{
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 9999;
      background: linear-gradient(135deg, #0E6B50 0%, #0a4d3a 100%);
      color: #ffffff;
      border: 2px solid #D4AF37;
      border-radius: 12px;
      padding: 10px 24px;
      font-size: 10.5pt;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(14,107,80,0.35);
      letter-spacing: 0.4px;
      transition: all 0.2s ease;
    }}
    .print-btn:hover {{
      background: linear-gradient(135deg, #128262 0%, #0c5c45 100%);
      transform: translateY(-1px);
    }}

    /* Header */
    .header-container {{
      border-bottom: 2px solid #D4AF37;
      padding-bottom: 10px;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo-title-area {{
      display: flex;
      flex-direction: column;
    }}
    .inst-name {{
      font-size: 11pt;
      font-weight: 700;
      color: #0E6B50;
      letter-spacing: 0.3px;
      text-transform: uppercase;
    }}
    .report-title {{
      font-size: 15pt;
      font-weight: 800;
      color: #1E1A12;
      margin: 2px 0;
    }}
    .arabic-title {{
      font-family: 'Amiri', 'Traditional Arabic', serif;
      font-size: 14pt;
      color: #B88917;
      direction: rtl;
    }}

    /* Teacher Info Card */
    .info-bar {{
      background: #fdfcf9;
      border: 1px solid #e2dccf;
      border-left: 4px solid #0E6B50;
      border-radius: 8px;
      padding: 10px 14px;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .teacher-name {{
      font-size: 13pt;
      font-weight: 800;
      color: #0E6B50;
    }}
    .date-range-badge {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
      padding: 4px 12px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 9pt;
    }}

    /* Metrics Summary Cards */
    .stats-grid {{
      display: flex;
      gap: 10px;
      margin-bottom: 16px;
      width: 100%;
    }}
    .stat-card {{
      flex: 1;
      background: #fdfcf9;
      border: 1px solid #e2dccf;
      border-radius: 8px;
      padding: 8px 12px;
      text-align: center;
    }}
    .stat-label {{
      font-size: 7.5pt;
      font-weight: 700;
      color: #718096;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 3px;
    }}
    .stat-val {{
      font-size: 14pt;
      font-weight: 800;
    }}

    /* Table */
    .table-container {{
      width: 100%;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      overflow: hidden;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    th {{
      background: #0E6B50;
      color: #ffffff;
      font-size: 8.5pt;
      font-weight: 700;
      padding: 7px 10px;
      border-bottom: 1px solid #cbd5e1;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}
    td {{
      padding: 6px 10px;
      border-bottom: 1px solid #e2e8f0;
      font-size: 8.5pt;
    }}
    tr:last-child td {{
      border-bottom: none;
    }}

    /* Status Badges */
    .badge-present {{
      display: inline-block;
      background-color: #dcfce7;
      color: #15803d;
      border: 1px solid #bbf7d0;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 8pt;
      font-weight: 700;
    }}
    .badge-absent {{
      display: inline-block;
      background-color: #fee2e2;
      color: #b91c1c;
      border: 1px solid #fecaca;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 8pt;
      font-weight: 700;
    }}
    .badge-sunday {{
      display: inline-block;
      background-color: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 7pt;
      font-weight: 700;
      margin-left: 4px;
    }}
    .time-present {{
      color: #0E6B50;
    }}
    .time-absent {{
      color: #a0aec0;
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <div class="header-container">
    <div class="logo-title-area">
      <div class="inst-name">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div class="report-title">Teacher Attendance Report</div>
      <div style="font-size: 8.5pt; color: #718096;">Mukhayyam Al-Quran Al-Kareem</div>
    </div>
    <div class="arabic-title">
      تقرير حضور المعلم التفصيلي
    </div>
  </div>

  <!-- Teacher Info Bar -->
  <div class="info-bar">
    <div>
      <span style="font-size: 8pt; color: #718096; text-transform: uppercase; font-weight: bold; display: block;">Teacher Name / اسم المعلم:</span>
      <span class="teacher-name">{escape(teacher_name)}</span>{username_sub}
    </div>
    <div>
      <span style="font-size: 8pt; color: #718096; text-transform: uppercase; font-weight: bold; display: block; text-align: right;">Period:</span>
      <span class="date-range-badge">📅 {escape(range_str)}</span>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="stats-grid">
    <div class="stat-card" style="border-left: 3px solid #64748b;">
      <div class="stat-label">Total Days (incl. Sundays)</div>
      <div class="stat-val" style="color: #334155;">{total_days}</div>
    </div>
    <div class="stat-card" style="border-left: 3px solid #16a34a;">
      <div class="stat-label">Present Days</div>
      <div class="stat-val" style="color: #16a34a;">{present_days}</div>
    </div>
    <div class="stat-card" style="border-left: 3px solid #dc2626;">
      <div class="stat-label">Absent Days</div>
      <div class="stat-val" style="color: #dc2626;">{absent_days}</div>
    </div>
    <div class="stat-card" style="border-left: 3px solid #0E6B50;">
      <div class="stat-label">Attendance Rate</div>
      <div class="stat-val" style="color: #0E6B50;">{pct}%</div>
    </div>
  </div>

  <!-- Day-wise Table -->
  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th style="width: 6%; text-align: center;">#</th>
          <th style="width: 25%;">Day</th>
          <th style="width: 25%;">Date</th>
          <th style="width: 20%; text-align: center;">Status</th>
          <th style="width: 24%; text-align: center;">Login / Tasmee Time</th>
        </tr>
      </thead>
      <tbody>
        {table_rows_str}
      </tbody>
    </table>
  </div>

  <!-- Print Button -->
  <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>

</body>
</html>
"""





