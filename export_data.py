import os
import csv
from datetime import datetime
import requests
import toml

def load_credentials():
    """Loads Supabase credentials from .streamlit/secrets.toml or environment variables."""
    # Try loading from .streamlit/secrets.toml
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            url = secrets.get("SUPABASE_URL")
            key = secrets.get("SUPABASE_KEY")
            if url and key:
                return url.strip(), key.strip()
        except Exception as e:
            print(f"[-] Error reading {secrets_path}: {e}")

    # Fallback to environment variables
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url.strip(), key.strip()

    return None, None

def fetch_table(url, key, table):
    """Fetches all rows from a Supabase PostgREST table."""
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    # Fetch in chunks or single request (free tier limit is usually plenty for this size)
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    try:
        response = requests.get(endpoint, headers=headers, params={"select": "*"}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[-] Failed to fetch table '{table}': {e}")
        return None

def save_to_csv(data, table_name, folder):
    """Saves a list of dictionaries to a CSV file."""
    if not data:
        print(f"[!] No data to save for table '{table_name}'. Skipping.")
        return

    file_path = os.path.join(folder, f"{table_name}.csv")
    try:
        # Determine headers from the keys of the first row
        headers = list(data[0].keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"[+] Saved {len(data)} rows to '{file_path}'")
    except Exception as e:
        print(f"[-] Failed to write to CSV for '{table_name}': {e}")

def main():
    print("[*] Starting Supabase Data Exporter...")
    url, key = load_credentials()
    if not url or not key:
        print("[-] Error: Supabase credentials not found!")
        print("    Please ensure you have a .streamlit/secrets.toml file with:")
        print("    SUPABASE_URL = \"...\"")
        print("    SUPABASE_KEY = \"...\"")
        print("    Or set the environment variables SUPABASE_URL and SUPABASE_KEY.")
        return

    # Create backups folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join("backups", f"backup_{timestamp}")
    os.makedirs(backup_folder, exist_ok=True)
    print(f"[+] Created backup directory: {backup_folder}")

    tables = [
        "students",
        "listening_sessions",
        "mistake_counts",
        "mistake_events",
        "jadeed_entries",
        "jadeed_daily",
        "takhteet_daily"
    ]

    for table in tables:
        print(f"[*] Fetching table: {table}...")
        data = fetch_table(url, key, table)
        if data is not None:
            save_to_csv(data, table, backup_folder)

    print("\n[+] Data export complete! You can find your CSV files in the backups/ folder.")

if __name__ == "__main__":
    main()
