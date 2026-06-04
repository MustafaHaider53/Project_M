from __future__ import annotations

from html import escape
from typing import Any, Dict, List
from datetime import datetime


def _to_arabic_numeral(n: int) -> str:
    return str(n)


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


def _format_takhteet_cell(tak: Dict[str, str]) -> str:
    parts = []
    m = tak.get("murajat", "").strip()
    j = tak.get("juzulhali", "").strip()
    jd = tak.get("jadeed", "").strip()

    if m:
        parts.append(f'<div class="hw-item"><span class="hw-prefix">M:</span> {escape(m)}</div>')
    if j:
        parts.append(f'<div class="hw-item"><span class="hw-prefix">J:</span> {escape(j)}</div>')
    if jd:
        parts.append(f'<div class="hw-item"><span class="hw-prefix">D:</span> {escape(jd)}</div>')

    if not parts:
        return '<span class="muted">-</span>'
    return "".join(parts)


def build_report_html(student_name: str, rows: List[Dict[str, Any]]) -> str:
    # Ensure rows are sorted by date ascending (Day 1 to Day 30)
    sorted_rows = sorted(rows, key=lambda x: x.get("activity_date", ""))
    
    month_year_str = _get_month_year_str(sorted_rows)

    table_rows = []
    for idx, r in enumerate(sorted_rows):
        activity_date = r.get("activity_date", "")
        
        # Format the date number (Arabic ١, ٢, ٣...)
        date_num = _to_arabic_numeral(idx + 1)
        
        # Calendar date suffix e.g., 04/05
        date_sub = ""
        if len(activity_date) == 10:
            date_sub = f"{activity_date[8:10]}/{activity_date[5:7]}"
            
        murajat = r.get("murajat", [])
        juzulhali = r.get("juzulhali", [])
        jadeed = r.get("jadeed", [])
        
        # Calculate sub-rows needed for this day to keep grid columns aligned
        N_rows = max(len(murajat), len(juzulhali), len(jadeed), 1)
        
        for sub_idx in range(N_rows):
            cells = []
            
            # 1. Date column (rowspanned)
            if sub_idx == 0:
                cells.append(
                    f'<td class="date-col col-date" rowspan="{N_rows}">'
                    f'  <div class="day-number">{date_num}</div>'
                    f'  <div class="day-date">{date_sub}</div>'
                    f'</td>'
                )
                
            # 2. Murajat columns (Juz/Surah, Talqeen, Tanbeeh, Repeat, Mutashabehat, Grade)
            if sub_idx < len(murajat):
                m = murajat[sub_idx]
                surah_name = m.get("surah_name_ar") or m.get("surat") or ""
                # If Surah name contains the number (like "1 - Al-Fatiha"), clean it up or translate
                if surah_name and " - " in surah_name:
                    parts = surah_name.split(" - ")
                    surah_name = parts[1] if len(parts) > 1 else surah_name
                    
                talqeen = _to_arabic_numeral(m.get("talqeen", 0)) if m.get("talqeen", 0) > 0 else "0"
                tanbeeh = _to_arabic_numeral(m.get("tanbeeh", 0)) if m.get("tanbeeh", 0) > 0 else "0"
                repeat = _to_arabic_numeral(m.get("repeat_mistake", 0)) if m.get("repeat_mistake", 0) > 0 else "0"
                mutashabehat = _to_arabic_numeral(m.get("mutashabehat", 0)) if m.get("mutashabehat", 0) > 0 else "0"
                marks = f"{m.get('marks', 0.0):.1f}"
                marks_ar = _to_arabic_numeral(int(float(marks))) + "." + _to_arabic_numeral(int(round((float(marks) - int(float(marks))) * 10)))
                
                cells.append(f'<td class="text-left col-murajat" style="font-weight: 600;">{escape(surah_name)}</td>')
                cells.append(f'<td class="col-murajat">{talqeen}</td>')
                cells.append(f'<td class="col-murajat">{tanbeeh}</td>')
                cells.append(f'<td class="col-murajat">{repeat}</td>')
                cells.append(f'<td class="col-murajat">{mutashabehat}</td>')
                cells.append(f'<td class="col-murajat" style="font-weight: bold; color: #1b4d3e;">{marks_ar}</td>')
            else:
                cells.extend(['<td class="col-murajat"></td>'] * 6)
                
            # 3. Juzulhali columns (Page, Talqeen, Tanbeeh, Repeat, Mutashabehat, Grade)
            if sub_idx < len(juzulhali):
                j = juzulhali[sub_idx]
                page = _to_arabic_numeral(j.get("page_number", 0)) if j.get("page_number", 0) > 0 else "-"
                talqeen = _to_arabic_numeral(j.get("talqeen", 0)) if j.get("talqeen", 0) > 0 else "0"
                tanbeeh = _to_arabic_numeral(j.get("tanbeeh", 0)) if j.get("tanbeeh", 0) > 0 else "0"
                repeat = _to_arabic_numeral(j.get("repeat_mistake", 0)) if j.get("repeat_mistake", 0) > 0 else "0"
                mutashabehat = _to_arabic_numeral(j.get("mutashabehat", 0)) if j.get("mutashabehat", 0) > 0 else "0"
                marks = f"{j.get('marks', 0.0):.1f}"
                marks_ar = _to_arabic_numeral(int(float(marks))) + "." + _to_arabic_numeral(int(round((float(marks) - int(float(marks))) * 10)))
                
                cells.append(f'<td class="col-juzulhali">{page}</td>')
                cells.append(f'<td class="col-juzulhali">{talqeen}</td>')
                cells.append(f'<td class="col-juzulhali">{tanbeeh}</td>')
                cells.append(f'<td class="col-juzulhali">{repeat}</td>')
                cells.append(f'<td class="col-juzulhali">{mutashabehat}</td>')
                cells.append(f'<td class="col-juzulhali" style="font-weight: bold; color: #1b4d3e;">{marks_ar}</td>')
            else:
                cells.extend(['<td class="col-juzulhali"></td>'] * 6)
                
            # 4. Jadeed columns (Surah, Page, Ayah, Volume)
            if sub_idx < len(jadeed):
                jd = jadeed[sub_idx]
                surah_name = jd.get("surah_name_ar") or jd.get("surat") or ""
                if surah_name and " - " in surah_name:
                    parts = surah_name.split(" - ")
                    surah_name = parts[1] if len(parts) > 1 else surah_name
                    
                page = _to_arabic_numeral(jd.get("page_number", 0)) if jd.get("page_number", 0) > 0 else "-"
                ayah = _to_arabic_numeral(jd.get("ayah_number", 0)) if jd.get("ayah_number", 0) > 0 else "-"
                volume = jd.get("volume") or "-"
                
                cells.append(f'<td class="text-left col-jadeed">{escape(surah_name)}</td>')
                cells.append(f'<td class="col-jadeed">{page}</td>')
                cells.append(f'<td class="col-jadeed">{ayah}</td>')
                cells.append(f'<td class="col-jadeed">{escape(volume)}</td>')
            else:
                cells.extend(['<td class="col-jadeed"></td>'] * 4)
                
            # 5. Homework/Takhteet column (rowspanned)
            if sub_idx == 0:
                cells.append(
                    f'<td class="hw-col col-takhteet" rowspan="{N_rows}">'
                    f'  {_format_takhteet_cell(r.get("takhteet", {}))}'
                    f'</td>'
                )
                
            is_last_sub = (sub_idx == N_rows - 1)
            row_class = ' class="day-separator"' if is_last_sub else ''
            table_rows.append(f"<tr{row_class}>{''.join(cells)}</tr>")

    return f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8"/>
  <title>Monthly Recitation Report - {escape(student_name)}</title>
  <style>
    @page {{
      size: A4 landscape;
      margin: 5mm 6mm 5mm 6mm;
    }}
    @media print {{
      .print-btn {{ display: none !important; }}
    }}
    .print-btn {{
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 9999;
      background: linear-gradient(135deg, #D4AF37 0%, #B88917 100%);
      color: #1E1A12;
      border: 2px solid #0E6B50;
      border-radius: 12px;
      padding: 10px 24px;
      font-size: 10.5pt;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(212,175,55,0.45), 0 2px 6px rgba(14,107,80,0.2);
      letter-spacing: 0.4px;
      transition: all 0.2s ease;
    }}
    .print-btn:hover {{
      background: linear-gradient(135deg, #e0bf4a 0%, #c99b1e 100%);
      box-shadow: 0 6px 24px rgba(212,175,55,0.55), 0 2px 8px rgba(14,107,80,0.25);
      transform: translateY(-1px);
    }}
    body {{
      font-family: "Segoe UI", Arial, sans-serif;
      direction: ltr;
      color: #1e1a12;
      font-size: 6.8pt;
      line-height: 1.15;
      margin: 0;
      padding: 0;
      background-color: #ffffff;
    }}
    .header-container {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
      border-bottom: 1.5px solid #1b4d3e;
      padding-bottom: 3px;
    }}
    .header-title {{
      font-size: 11pt;
      font-weight: bold;
      color: #1b4d3e;
      margin: 0;
      text-align: center;
    }}
    .meta-item {{
      font-size: 8pt;
      font-weight: bold;
      color: #333;
      width: 33%;
    }}
    .meta-item.right-align {{
      text-align: right;
    }}
    .meta-item.center-align {{
      text-align: center;
    }}
    .meta-item.left-align {{
      text-align: left;
    }}
    .meta-val {{
      font-weight: normal;
      color: #111;
      border-bottom: 1px dashed #666;
      padding: 0 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin-top: 1px;
      border: 1px solid #1b4d3e;
    }}
    th {{
      color: #1b4d3e;
      font-weight: bold;
      border: 0.5px solid #1b4d3e;
      font-size: 6.8pt;
      padding: 2px 1px;
      text-align: center;
      vertical-align: middle;
    }}
    thead tr:nth-child(1) th {{
      background-color: #f5da8b;
    }}
    thead tr:nth-child(2) th {{
      background-color: #fff4cc;
    }}
    td {{
      border: 0.5px solid #a89f91;
      padding: 1.8px 2px;
      vertical-align: middle;
      font-size: 6.5pt;
      text-align: center;
      height: 10px;
    }}
    .col-date {{
      background-color: #fff4cc !important;
    }}
    .col-murajat {{
      background-color: #ebfaeb !important;
    }}
    .col-juzulhali {{
      background-color: #ffefe2 !important;
    }}
    .col-jadeed {{
      background-color: #f4ecff !important;
    }}
    .col-takhteet {{
      background-color: #e8f3ff !important;
    }}
    .date-col {{
      font-weight: bold;
      color: #1b4d3e;
      border-left: 0.5px solid #1b4d3e;
      border-right: 0.5px solid #1b4d3e;
      padding: 0;
    }}
    .day-number {{
      font-size: 8.5pt;
      margin-bottom: 0px;
    }}
    .day-date {{
      font-size: 5.2pt;
      color: #555;
      font-weight: normal;
    }}
    .text-left {{
      text-align: left;
      padding-left: 4px;
    }}
    .day-separator td {{
      border-bottom: 2px solid #1b4d3e !important;
    }}
    .muted {{
      color: #a89f91;
      font-style: italic;
    }}
    .hw-col {{
      text-align: left;
      padding-left: 4px;
    }}
    .hw-item {{
      text-align: left;
      margin-bottom: 1px;
      line-height: 1.1;
    }}
    .hw-item:last-child {{
      margin-bottom: 0;
    }}
    .hw-prefix {{
      font-weight: bold;
      color: #1b4d3e;
    }}
  </style>
</head>
<body>
  <!-- Themed Banner -->
  <div style="
    background: linear-gradient(135deg, #0E6B50 0%, #1b4d3e 60%, #0a3d2e 100%);
    border-bottom: 3px solid #D4AF37;
    padding: 7px 14px 6px 14px;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  ">
    <div style="text-align:left;">
      <div style="color:#D4AF37; font-size:7pt; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; opacity:0.85;">Student</div>
      <div style="color:#FBF6EA; font-size:10pt; font-weight:800; letter-spacing:0.3px;">{escape(student_name)}</div>
    </div>
    <div style="text-align:center; flex:1; padding: 0 10px;">
      <div style="color:#D4AF37; font-size:8pt; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; opacity:0.75;">Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>
      <div style="color:#FBF6EA; font-size:12pt; font-weight:900; letter-spacing:0.5px; margin-top:1px;">Monthly Recitation Report</div>
    </div>
    <div style="text-align:right;">
      <div style="color:#D4AF37; font-size:7pt; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; opacity:0.85;">Month</div>
      <div style="color:#FBF6EA; font-size:10pt; font-weight:800; letter-spacing:0.3px;">{escape(month_year_str)}</div>
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th rowspan="2" style="width: 4.5%;">Date</th>
        <th colspan="6" style="width: 27%;">Murajat</th>
        <th colspan="6" style="width: 22%;">Juzulhali</th>
        <th colspan="4" style="width: 27%;">Jadeed</th>
        <th rowspan="2" style="width: 19.5%;">Takhteet</th>
      </tr>
      <tr>
        <!-- Murajat -->
        <th style="width: 11%;">Juz/Surah</th>
        <th style="width: 3.2%;">Talqeen</th>
        <th style="width: 3.2%;">Tanbeeh</th>
        <th style="width: 3.2%;">Repeat</th>
        <th style="width: 3.2%;">Mutash.</th>
        <th style="width: 3.2%;">Grade</th>
        <!-- Juzulhali -->
        <th style="width: 6%;">Page</th>
        <th style="width: 3.2%;">Talqeen</th>
        <th style="width: 3.2%;">Tanbeeh</th>
        <th style="width: 3.2%;">Repeat</th>
        <th style="width: 3.2%;">Mutash.</th>
        <th style="width: 3.2%;">Grade</th>
        <!-- Jadeed -->
        <th style="width: 12%;">Surah</th>
        <th style="width: 5%;">Page</th>
        <th style="width: 5%;">Ayah</th>
        <th style="width: 5%;">Volume</th>
      </tr>
    </thead>
    <tbody>
      {"".join(table_rows)}
    </tbody>
  </table>

  <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>

</body>
</html>
"""


def export_html_to_pdf_bytes(html: str) -> bytes:
    """
    Uses Playwright (Chromium) for reliable single-page A4 landscape PDF export.
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
