"""Bulk validate and upload students from an Excel (.xlsx) or CSV (.csv) file into Supabase.

Supports:
  1. Validation & dry-run preview (default)
  2. Generating a clean SQL seed file (--sql-out supabase/seed_students.sql)
  3. Direct batched upsert into Supabase REST API (--upload --url ... --key ...)
"""
from __future__ import annotations

import argparse
import csv
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


NAME_ALIASES = ("full_name", "fullname", "student_name", "student name", "name", "student")
ITS_ALIASES = ("its", "its_id", "its id", "its_no", "its no", "its number", "its_number")
EMAIL_ALIASES = ("email", "parent_email", "parent email", "email_address", "email address", "mail")


def _norm_header(h: Any) -> str:
    return " ".join(str(h or "").strip().lower().replace("-", "_").split())


def _pick(row: Dict[str, str], aliases: tuple[str, ...]) -> str:
    for a in aliases:
        if a in row and row[a] != "":
            return row[a]
    return ""


def _clean_its(raw: str) -> str:
    s = str(raw or "").strip()
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits or s


def read_input_file(path: Path) -> List[Dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = []
            for r in reader:
                if not any(str(v or "").strip() for v in r.values()):
                    continue
                rows.append({_norm_header(k): str(v or "").strip() for k, v in r.items() if k})
            return rows

    if suffix in (".xlsx", ".xlsm"):
        import openpyxl

        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        header_raw = next(it, None)
        if not header_raw:
            return []
        headers = [_norm_header(h) for h in header_raw]
        rows = []
        for vals in it:
            if all(v in (None, "") for v in vals):
                continue
            rows.append({
                h: ("" if v is None else str(v).strip())
                for h, v in zip(headers, vals)
                if h
            })
        return rows

    raise ValueError(f"Unsupported file format '{suffix}'. Please provide .xlsx or .csv.")


def parse_and_validate(raw_rows: List[Dict[str, str]]) -> tuple[List[Dict[str, Optional[str]]], List[str]]:
    students: List[Dict[str, Optional[str]]] = []
    warnings: List[str] = []
    seen_names: Dict[str, int] = {}
    seen_its: Dict[str, str] = {}

    for idx, r in enumerate(raw_rows, start=2):
        full_name = " ".join(_pick(r, NAME_ALIASES).split())
        its = _clean_its(_pick(r, ITS_ALIASES))
        email = _pick(r, EMAIL_ALIASES).strip().lower()

        if not full_name:
            warnings.append(f"Row {idx}: skipped (missing student name)")
            continue

        if not its:
            warnings.append(f"Row {idx} ({full_name}): missing ITS")
        elif not (its.isdigit() and len(its) == 8):
            warnings.append(f"Row {idx} ({full_name}): unusual ITS '{its}' (expected 8 digits)")
        elif its in seen_its and seen_its[its].lower() != full_name.lower():
            warnings.append(f"Row {idx} ({full_name}): duplicate ITS '{its}' (already used by {seen_its[its]})")
        else:
            seen_its[its] = full_name

        key = full_name.lower()
        record = {
            "full_name": full_name,
            "its": its or None,
            "email": email or None,
        }
        if key in seen_names:
            warnings.append(f"Row {idx} ({full_name}): duplicate name — overwriting earlier row {seen_names[key] + 2}")
            students[seen_names[key]] = record
        else:
            seen_names[key] = len(students)
            students.append(record)

    return students, warnings


def _sql_lit(val: Optional[str]) -> str:
    if val is None or val == "":
        return "NULL"
    return "'" + val.replace("'", "''") + "'"


def write_sql_seed(students: List[Dict[str, Optional[str]]], sql_path: Path) -> None:
    sql_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "-- Auto-generated student bulk seed (safe to re-run)",
        "insert into public.students (full_name, its, email)",
        "values",
    ]
    val_lines = []
    for s in students:
        val_lines.append(f"  ({_sql_lit(s['full_name'])}, {_sql_lit(s['its'])}, {_sql_lit(s['email'])})")
    lines.append(",\n".join(val_lines))
    lines.append("on conflict (full_name) do update")
    lines.append("set its = coalesce(excluded.its, public.students.its),")
    lines.append("    email = coalesce(excluded.email, public.students.email);")
    sql_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def upload_to_supabase(students: List[Dict[str, Optional[str]]], url: str, key: str, batch_size: int = 200) -> int:
    endpoint = f"{url.rstrip('/')}/rest/v1/students?on_conflict=full_name"
    ctx = ssl.create_default_context()
    uploaded = 0

    for start in range(0, len(students), batch_size):
        batch = students[start : start + batch_size]
        payload = json.dumps(batch).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                if resp.status not in (200, 201, 204):
                    raise RuntimeError(f"Unexpected HTTP status {resp.status}")
                uploaded += len(batch)
                print(f"  [+] Upserted batch {start + 1}-{start + len(batch)} ({uploaded}/{len(students)})")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore") if e.fp else str(e)
            raise RuntimeError(f"Supabase HTTP {e.code}: {body}") from e

    return uploaded


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate & upload students from Excel/CSV into Supabase")
    ap.add_argument("--file", required=True, type=Path, help="Path to student Excel (.xlsx) or CSV (.csv)")
    ap.add_argument("--sql-out", type=Path, default=None, help="Optional path to write SQL seed file")
    ap.add_argument("--upload", action="store_true", help="Upload directly to Supabase REST API")
    ap.add_argument("--url", default="", help="Target Supabase project URL (required with --upload)")
    ap.add_argument("--key", default="", help="Target Supabase API key (required with --upload)")
    args = ap.parse_args()

    if not args.file.exists():
        print(f"[ERROR] File not found: {args.file}")
        return 1

    raw_rows = read_input_file(args.file)
    print(f"[*] Read {len(raw_rows)} non-empty rows from {args.file.name}")

    students, warnings = parse_and_validate(raw_rows)
    with_its = sum(1 for s in students if s["its"])
    with_email = sum(1 for s in students if s["email"])

    print(f"[*] Valid unique students: {len(students)} (with ITS: {with_its}, with Email: {with_email})")
    if warnings:
        print(f"\n⚠️  {len(warnings)} validation warning(s):")
        for w in warnings[:40]:
            print(f"  - {w}")
        if len(warnings) > 40:
            print(f"  ... and {len(warnings) - 40} more.")

    print("\n📋 Preview (first 10 students):")
    for s in students[:10]:
        print(f"  • {s['full_name']} | ITS: {s['its'] or '-'} | Email: {s['email'] or '-'}")

    if args.sql_out:
        write_sql_seed(students, args.sql_out)
        print(f"\n✅ SQL seed file written to: {args.sql_out}")

    if args.upload:
        if not args.url or not args.key:
            print("\n[ERROR] --url and --key are required when using --upload.")
            return 1
        print(f"\n🚀 Uploading {len(students)} students to {args.url}...")
        count = upload_to_supabase(students, args.url, args.key)
        print(f"\n✅ Done! Upserted {count} students into public.students.")
    elif not args.sql_out:
        print("\nℹ️ Dry-run complete. Re-run with --sql-out <file.sql> or --upload --url <URL> --key <KEY>.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
