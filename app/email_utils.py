from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Tuple
from datetime import datetime
import streamlit as st


AHKAM_MAP = {
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
    "makhraj_thaal": "ذ",
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

def _format_ahkam_email(counts: Dict[str, Any]) -> str:
    badges = []
    for col, label in AHKAM_MAP.items():
        val = counts.get(col, 0)
        if val > 0:
            lbl = f"{label}" if val == 1 else f"{label} ({val})"
            badges.append(
                f'<span style="display: inline-block; padding: 2px 6px; font-size: 10px; font-weight: bold; border-radius: 12px; margin: 2px; white-space: nowrap; background-color: #fff5f5; color: #9b2c2c; border: 1px solid #fed7d7;">{lbl}</span>'
            )
    return "".join(badges)

def _format_makharij_email(counts: Dict[str, Any]) -> str:
    badges = []
    for col, char in MAKHRAJ_CHARS.items():
        val = counts.get(col, 0)
        if val > 0:
            lbl = f"{char}" if val == 1 else f"{char} ({val})"
            badges.append(
                f'<span style="display: inline-block; padding: 2px 6px; font-size: 11px; font-weight: bold; border-radius: 12px; margin: 2px; white-space: nowrap; background-color: #ebf8ff; color: #2b6cb0; border: 1px solid #bee3f8; font-family: \'Amiri\', \'Traditional Arabic\', serif;">{lbl}</span>'
            )
    return "".join(badges)


def generate_progress_html(summary: Dict[str, Any]) -> str:
    student_name = summary.get("student_name", "Student")
    activity_date = summary.get("activity_date", "")
    try:
        dt = datetime.strptime(activity_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%A, %B %d, %Y")
    except Exception:
        formatted_date = activity_date

    # 1. Murajat Section
    murajat_html = ""
    if summary.get("murajat"):
        murajat_rows = ""
        for m in summary["murajat"]:
            surah = m.get("surahs") or {}
            surah_name = surah.get("name_en") or "Surah"
            surah_ar = surah.get("name_ar") or ""
            page = m.get("page_number", 0)
            if page > 0:
                surah_display = f"{surah_name} (Page {page})"
            else:
                surah_display = surah_name
            counts = m.get("mistake_counts") or {}
            if isinstance(counts, list):
                counts = counts[0] if counts else {}
            talqeen = counts.get("talqeen", 0)
            tanbeeh = counts.get("tanbeeh", 0)
            irab = counts.get("irab", 0)
            repeat = counts.get("repeat_mistake", 0)
            mutashabehat = counts.get("mutashabehat", 0)
            
            # format mistakes
            ahkam_str = _format_ahkam_email(counts)
            makharij_str = _format_makharij_email(counts)
            
            mistakes_detail = ""
            if ahkam_str or makharij_str:
                mistakes_detail += '<div style="margin-top: 5px; padding-top: 4px; border-top: 1px dotted #e0dcd5; text-align: left; line-height: 1.5;">'
                if ahkam_str:
                    mistakes_detail += ahkam_str
                if makharij_str:
                    mistakes_detail += makharij_str
                mistakes_detail += '</div>'
            
            # calculate grade/marks (consistent with 10 - 0.5 * talqeen - 0.25 * tanbeeh)
            is_zero = bool(counts.get("is_zero_marks", False))
            if is_zero:
                marks = 0.0
            else:
                marks = 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh)
                if marks < 0:
                    marks = 0.0
            murajat_rows += f"""
            <tr>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; font-weight: bold; color: #1b4d3e;">
                    {surah_display} <span style="font-size: 11px; color: #888; display: block;">({surah_ar})</span>
                    {mistakes_detail}
                </td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{talqeen}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{tanbeeh}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{irab}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{repeat}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{mutashabehat}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; font-weight: bold; color: #1b4d3e;">{marks:.1f}/10</td>
            </tr>
            """
        
        murajat_html = f"""
        <h3 style="color: #1b4d3e; border-bottom: 2px solid #c5a880; padding-bottom: 4px; margin-top: 25px;">1. Murajat </h3>
        <div style="width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background-color: #f7f5f0; color: #1b4d3e;">
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: left;">Surah</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">T</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">Tb</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">I</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">R</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">M</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 55px;">Grade</th>
                    </tr>
                </thead>
                <tbody>
                    {murajat_rows}
                </tbody>
            </table>
        </div>
        <div style="margin-top: 12px; padding: 10px 12px; background-color: #fdfcf9; border: 1px solid #e8e4db; border-radius: 6px; font-size: 12px; line-height: 1.5; color: #444;">
            <strong style="color: #1b4d3e; font-size: 13px; display: block; margin-bottom: 4px;">Table Columns Explanation:</strong>
            <span style="display: inline-block; margin-right: 12px;"><strong>T</strong>: Talqeen </span>
            <span style="display: inline-block; margin-right: 12px;"><strong>Tb</strong>: Tanbeeh </span>
            <span style="display: inline-block; margin-right: 12px;"><strong>I</strong>: I'rab </span>
            <span style="display: inline-block; margin-right: 12px;"><strong>R</strong>: Repeat </span>
            <span style="display: inline-block;"><strong>M</strong>: Mutashabehat (Similar Verses)</span>
        </div>
        """

    # 2. Juzulhali Section
    juzulhali_html = ""
    if summary.get("juzulhali"):
        juzulhali_rows = ""
        for j in summary["juzulhali"]:
            surah = j.get("surahs") or {}
            surah_name = surah.get("name_en") or ""
            page = j.get("page_number") or "-"
            if surah_name:
                recitation_display = f"{surah_name} (Page {page})"
            else:
                recitation_display = f"Page {page}"
            counts = j.get("mistake_counts") or {}
            if isinstance(counts, list):
                counts = counts[0] if counts else {}
            talqeen = counts.get("talqeen", 0)
            tanbeeh = counts.get("tanbeeh", 0)
            irab = counts.get("irab", 0)
            repeat = counts.get("repeat_mistake", 0)
            mutashabehat = counts.get("mutashabehat", 0)
            
            # format mistakes
            ahkam_str = _format_ahkam_email(counts)
            makharij_str = _format_makharij_email(counts)
            
            mistakes_detail = ""
            if ahkam_str or makharij_str:
                mistakes_detail += '<div style="margin-top: 5px; padding-top: 4px; border-top: 1px dotted #e0dcd5; text-align: left; line-height: 1.5;">'
                if ahkam_str:
                    mistakes_detail += ahkam_str
                if makharij_str:
                    mistakes_detail += makharij_str
                mistakes_detail += '</div>'
            
            is_zero = bool(counts.get("is_zero_marks", False))
            if is_zero:
                marks = 0.0
            else:
                marks = 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh)
                if marks < 0:
                    marks = 0.0
            juzulhali_rows += f"""
            <tr>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; font-weight: bold; color: #1b4d3e; text-align: center;">
                    {recitation_display}
                    {mistakes_detail}
                </td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{talqeen}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{tanbeeh}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{irab}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{repeat}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center;">{mutashabehat}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; font-weight: bold; color: #1b4d3e;">{marks:.1f}/10</td>
            </tr>
            """
        
        juzulhali_html = f"""
        <h3 style="color: #1b4d3e; border-bottom: 2px solid #c5a880; padding-bottom: 4px; margin-top: 25px;">2. Juzulhali </h3>
        <div style="width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background-color: #f7f5f0; color: #1b4d3e;">
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 65px;">Page</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">T</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">Tb</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">I</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">R</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 32px;">M</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px 4px; text-align: center; width: 55px;">Grade</th>
                    </tr>
                </thead>
                <tbody>
                    {juzulhali_rows}
                </tbody>
            </table>
        </div>
        <div style="margin-top: 12px; padding: 10px 12px; background-color: #fdfcf9; border: 1px solid #e8e4db; border-radius: 6px; font-size: 12px; line-height: 1.5; color: #444;">
            <strong style="color: #1b4d3e; font-size: 13px; display: block; margin-bottom: 4px;">Table Columns Explanation:</strong>
            <span style="display: inline-block; margin-right: 12px;"><strong>T</strong>: Talqeen (Prompt)</span>
            <span style="display: inline-block; margin-right: 12px;"><strong>Tb</strong>: Tanbeeh (Correction)</span>
            <span style="display: inline-block; margin-right: 12px;"><strong>I</strong>: I'rab (Grammar Accent)</span>
            <span style="display: inline-block; margin-right: 12px;"><strong>R</strong>: Repeat (Recurring Mistake)</span>
            <span style="display: inline-block;"><strong>M</strong>: Mutashabehat (Similar Verses)</span>
        </div>
        """

    # 3. Jadeed Section
    jadeed_html = ""
    if summary.get("no_jadeed"):
        jadeed_html = """
        <h3 style="color: #1b4d3e; border-bottom: 2px solid #c5a880; padding-bottom: 4px; margin-top: 25px;">3. Jadeed </h3>
        <p style="font-size: 13px; color: #666; font-style: italic;">No Jadeed lesson recorded for today.</p>
        """
    elif summary.get("jadeed"):
        jadeed_rows = ""
        for jd in summary["jadeed"]:
            surah = jd.get("surahs") or {}
            surah_name = surah.get("name_en") or "Surah"
            surah_ar = surah.get("name_ar") or ""
            page = jd.get("page_number") or "-"
            ayah = jd.get("ayah_number") or "-"
            volume = jd.get("volume") or "-"
            
            jadeed_rows += f"""
            <tr>
                <td style="border: 1px solid #e0dcd5; padding: 8px; font-weight: bold; color: #1b4d3e;">{surah_name} <span style="font-size: 11px; color: #888;">({surah_ar})</span></td>
                <td style="border: 1px solid #e0dcd5; padding: 8px; text-align: center;">Page {page}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px; text-align: center;">Ayah {ayah}</td>
                <td style="border: 1px solid #e0dcd5; padding: 8px; text-align: center; font-weight: 500;">{volume}</td>
            </tr>
            """
        
        jadeed_html = f"""
        <h3 style="color: #1b4d3e; border-bottom: 2px solid #c5a880; padding-bottom: 4px; margin-top: 25px;">3. Jadeed (New Lesson)</h3>
        <div style="width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background-color: #f7f5f0; color: #1b4d3e;">
                        <th style="border: 1px solid #e0dcd5; padding: 8px; text-align: left;">Surah</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px; text-align: center;">Page</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px; text-align: center;">Ayah</th>
                        <th style="border: 1px solid #e0dcd5; padding: 8px; text-align: center;">Volume</th>
                    </tr>
                </thead>
                <tbody>
                    {jadeed_rows}
                </tbody>
            </table>
        </div>
        """

    # 4. Takhteet Section
    takhteet_html = ""
    t = summary.get("takhteet") or {}
    t_murajat = t.get("murajat_text_raw", "").strip()
    t_juzulhali = t.get("juzulhali_text_raw", "").strip()
    t_jadeed = t.get("jadeed_text_raw", "").strip()

    if t_murajat or t_juzulhali or t_jadeed:
        takhteet_html = f"""
        <h3 style="color: #1b4d3e; border-bottom: 2px solid #c5a880; padding-bottom: 4px; margin-top: 25px;">4. Takhteet (Homework Assigned)</h3>
        <div style="font-size: 13px; background-color: #fcfbfa; border: 1px solid #e8e4db; border-radius: 4px; padding: 12px; margin-top: 10px;">
        """
        if t_murajat:
            takhteet_html += f"<p style='margin: 4px 0;'><b>Murajat Homework</b>: {t_murajat}</p>"
        if t_juzulhali:
            takhteet_html += f"<p style='margin: 4px 0;'><b>Juzulhali Homework</b>: {t_juzulhali}</p>"
        if t_jadeed:
            takhteet_html += f"<p style='margin: 4px 0;'><b>Jadeed Homework</b>: {t_jadeed}</p>"
        takhteet_html += "</div>"

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: 'Georgia', 'Times New Roman', serif;
      background-color: #f7f6f2;
      color: #333;
      margin: 0;
      padding: 0;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }}
    .email-container {{
      max-width: 600px;
      margin: 20px auto;
      background-color: #ffffff;
      border: 1px solid #e8e4db;
      border-radius: 8px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}
    .table-wrapper {{
      width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      margin-top: 10px;
    }}
    .responsive-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    @media screen and (max-width: 480px) {{
      .email-container {{
        width: 100% !important;
        margin: 10px 0 !important;
        border-radius: 0 !important;
        border: none !important;
        overflow: visible !important;
      }}
      .content {{
        padding: 15px !important;
      }}
      .header {{
        padding: 20px 15px !important;
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
      }}
      .responsive-table {{
        min-width: 580px !important;
      }}
    }}
    .header {{
      background-color: #1b4d3e;
      border-bottom: 4px solid #c5a880;
      padding: 25px;
      text-align: center;
      border-top-left-radius: 7px;
      border-top-right-radius: 7px;
    }}
    .header h1 {{
      color: #ffffff;
      margin: 0;
      font-size: 20px;
      letter-spacing: 1px;
      font-weight: normal;
    }}
    .header p {{
      color: #c5a880;
      margin: 5px 0 0 0;
      font-size: 13px;
      text-transform: uppercase;
    }}
    .content {{
      padding: 25px;
      line-height: 1.6;
    }}
    .footer {{
      background-color: #f7f5f0;
      border-top: 1px solid #e8e4db;
      padding: 15px;
      text-align: center;
      font-size: 11px;
      color: #777;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h1>
      <p>Daily Tasmee Report</p>
    </div>
    <div class="content">
      <p>Salaam Jameel <br><b>{student_name}</b>,</p>
      <p>Below is the summary of your Quran recitation progress and feedback for <b>{formatted_date}</b>:</p>
      
      {murajat_html}
      {juzulhali_html}
      {jadeed_html}
      {takhteet_html}
      
      <p style="margin-top: 25px; font-size: 13px; font-style: italic; color: #555; text-align: center;">
        "أَوْ زِدْ عَلَيْهِ وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا"
      </p>
    </div>
    <div class="footer">
      This is an automated progress report sent by Al Madrasa-tus-Saifiyah-tul-Burhaniyah.
    </div>
  </div>
</body>
</html>
"""


def generate_absence_html(summary: Dict[str, Any]) -> str:
    student_name = summary.get("student_name", "Student")
    activity_date = summary.get("activity_date", "")
    try:
        dt = datetime.strptime(activity_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%A, %B %d, %Y")
    except Exception:
        formatted_date = activity_date

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: 'Georgia', 'Times New Roman', serif;
      background-color: #f7f6f2;
      color: #333;
      margin: 0;
      padding: 0;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }}
    .email-container {{
      max-width: 600px;
      margin: 20px auto;
      background-color: #ffffff;
      border: 1px solid #e8e4db;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}
    @media screen and (max-width: 480px) {{
      .email-container {{
        width: 100% !important;
        margin: 10px 0 !important;
        border-radius: 0 !important;
        border: none !important;
      }}
      .content {{
        padding: 15px !important;
      }}
      .header {{
        padding: 20px 15px !important;
      }}
    }}
    .header {{
      background-color: #721c24; /* Crimson Red for alert */
      border-bottom: 4px solid #c5a880;
      padding: 25px;
      text-align: center;
    }}
    .header h1 {{
      color: #ffffff;
      margin: 0;
      font-size: 20px;
      letter-spacing: 1px;
      font-weight: normal;
    }}
    .header p {{
      color: #f8d7da;
      margin: 5px 0 0 0;
      font-size: 13px;
      text-transform: uppercase;
      font-weight: bold;
    }}
    .content {{
      padding: 25px;
      line-height: 1.6;
    }}
    .alert-box {{
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      color: #721c24;
      padding: 15px;
      border-radius: 4px;
      margin: 15px 0;
      font-size: 14px;
      font-weight: 500;
    }}
    .footer {{
      background-color: #f7f5f0;
      border-top: 1px solid #e8e4db;
      padding: 15px;
      text-align: center;
      font-size: 11px;
      color: #777;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h1>
      <p>URGENT: Absence Warning Notice</p>
    </div>
    <div class="content">
      <p>Salaam Jameel <br><b>{student_name}</b>,</p>
      
      <div class="alert-box">
        We noticed that you did not attend tasmee session today, <b>{formatted_date}</b>.
      </div>
      
      <p>Consistency, dedication, and daily presence are fundamental pillars of memorizing and retaining the Holy Quran. Missing classes or sessions without a valid, pre-approved excuse severely disrupts your progress and the discipline required for Hifz.</p>
      
      <p><b>CRITICAL WARNING:</b> Unexcused absences have serious consequences. Frequent or unexplained absence will lead to academic probation, parent-teacher reviews, or immediate suspension from the Madrasa program.</p>
      
      <p>Kindly contact your teacher immediately to explain your absence.</p>
      
      <p style="margin-top: 25px; font-weight: bold; color: #721c24;">
        Sincerely,<br>
        Al Madrasa-tus-Saifiyah-tul-Burhaniyah Administration
      </p>
    </div>
    <div class="footer">
      This is an official administrative notice. Please do not reply directly to this email.
    </div>
  </div>
</body>
</html>
"""


def send_daily_report_email(*, summary: Dict[str, Any], is_absent: bool) -> Tuple[bool, str]:
    """
    Sends the daily report email. Returns (success, message).
    """
    email_secrets = st.secrets.get("email")
    if not email_secrets:
        return False, "Email configuration ('email' block in st.secrets) is missing."

    smtp_server = email_secrets.get("smtp_server")
    smtp_port = email_secrets.get("smtp_port")
    sender_email = email_secrets.get("sender_email")
    sender_password = email_secrets.get("sender_password")

    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        return False, "SMTP credentials inside st.secrets['email'] are incomplete."

    recipient = summary.get("student_email")
    if not recipient or not recipient.strip():
        return False, f"No email address found for {summary.get('student_name', 'Student')}."

    student_name = summary.get("student_name", "Student")
    activity_date = summary.get("activity_date", "")

    # Build the message
    msg = MIMEMultipart("alternative")
    
    if is_absent:
        subject = f"URGENT: Absence Warning - {activity_date} ({student_name})"
        body_html = generate_absence_html(summary)
    else:
        subject = f"Daily Tasmee Report - {activity_date} ({student_name})"
        body_html = generate_progress_html(summary)

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    msg.attach(MIMEText(body_html, "html"))

    try:
        # Connect and send
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(str(smtp_server), int(smtp_port), timeout=15)
        else:
            server = smtplib.SMTP(str(smtp_server), int(smtp_port), timeout=15)
            server.ehlo()
            server.starttls()
        server.login(str(sender_email), str(sender_password))
        server.sendmail(str(sender_email), [str(recipient)], msg.as_string())
        server.close()
        return True, f"Email successfully sent to {recipient}."
    except Exception as e:
        return False, f"Failed to send email: {e}"


def send_monthly_report_email(*, student_name: str, recipient_email: str, rows: List[Dict[str, Any]], report_type: str, year: int, month: int) -> Tuple[bool, str]:
    """
    Sends the monthly category-focused report email. Returns (success, message).
    """
    email_secrets = st.secrets.get("email")
    if not email_secrets:
        return False, "Email configuration ('email' block in st.secrets) is missing."

    smtp_server = email_secrets.get("smtp_server")
    smtp_port = email_secrets.get("smtp_port")
    sender_email = email_secrets.get("sender_email")
    sender_password = email_secrets.get("sender_password")

    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        return False, "SMTP credentials inside st.secrets['email'] are incomplete."

    if not recipient_email or not recipient_email.strip():
        return False, f"No email address found for {student_name}."

    # Build the HTML content
    from app.report_pdf import build_report_html, _get_month_year_str
    month_year_str = _get_month_year_str(rows)
    
    body_html = build_report_html(student_name, rows, report_type)
    # Remove the print button
    body_html = body_html.replace('<button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>', '')

    # Set subject based on report type
    report_titles = {
        "murajat": "Monthly Murajat Report",
        "juzulhali": "Monthly Juzulhali Report",
        "jadeed": "Monthly Jadeed Report",
        "takhteet": "Monthly Takhteet Report"
    }
    title = report_titles.get(report_type.lower(), "Monthly Report")
    subject = f"{title} - {month_year_str} ({student_name})"

    # Build the message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    msg.attach(MIMEText(body_html, "html"))

    try:
        # Connect and send
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(str(smtp_server), int(smtp_port), timeout=15)
        else:
            server = smtplib.SMTP(str(smtp_server), int(smtp_port), timeout=15)
            server.ehlo()
            server.starttls()
        server.login(str(sender_email), str(sender_password))
        server.sendmail(str(sender_email), [str(recipient_email)], msg.as_string())
        server.close()
        return True, f"Monthly {report_type.capitalize()} report email successfully sent to {recipient_email}."
    except Exception as e:
        return False, f"Failed to send monthly email: {e}"


def send_takhteet_plan_email(*, student_name: str, recipient_email: str, plan_html: str, year: int, month: int, custom_message: str = None) -> Tuple[bool, str]:
    """
    Sends the generated monthly Takhteet plan email. Returns (success, message).
    """
    email_secrets = st.secrets.get("email")
    if not email_secrets:
        return False, "Email configuration ('email' block in st.secrets) is missing."

    smtp_server = email_secrets.get("smtp_server")
    smtp_port = email_secrets.get("smtp_port")
    sender_email = email_secrets.get("sender_email")
    sender_password = email_secrets.get("sender_password")

    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        return False, "SMTP credentials inside st.secrets['email'] are incomplete."

    if not recipient_email or not recipient_email.strip():
        return False, f"No email address found for {student_name}."

    import calendar
    month_name = calendar.month_name[month]
    subject = f"Monthly Jadeed Takhteet Plan - {month_name} {year} ({student_name})"

    # Clean up printable actions and embed motivational intro for the parent email
    plan_html = plan_html.replace('<button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>', '')
    
    if custom_message and custom_message.strip():
        msg_body = custom_message.strip().replace('\n', '<br>')
    else:
        msg_body = "This is your monthly Jadeed Takhteet study plan. Consistent daily recitation builds strength and success in Hifz. Stay dedicated, keep reciting, and aim high!"

    intro_html = (
        "<div style=\"font-family: 'Outfit', 'Inter', 'Segoe UI', sans-serif; background-color: #faf8f5; "
        "padding: 18px; border-left: 4px solid #1b4d3e; border-radius: 6px; margin-bottom: 20px; "
        "font-size: 14px; line-height: 1.5; color: #333;\">"
        "<p style=\"margin: 0 0 8px 0; font-size: 15px; color: #1b4d3e;\"><b>Dear Parent & Student, Salaam Jameel!</b></p>"
        f"<p style=\"margin: 0;\">{msg_body}</p>"
        "</div>"
    )
    plan_html = plan_html.replace('<div class="planner-card">', f'<div class="planner-card">{intro_html}')

    # Build the message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    msg.attach(MIMEText(plan_html, "html"))

    try:
        # Connect and send
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(str(smtp_server), int(smtp_port), timeout=15)
        else:
            server = smtplib.SMTP(str(smtp_server), int(smtp_port), timeout=15)
            server.ehlo()
            server.starttls()
        server.login(str(sender_email), str(sender_password))
        server.sendmail(str(sender_email), [str(recipient_email)], msg.as_string())
        server.close()
        return True, f"Monthly Takhteet plan email successfully sent to {recipient_email}."
    except Exception as e:
        return False, f"Failed to send monthly email: {e}"
