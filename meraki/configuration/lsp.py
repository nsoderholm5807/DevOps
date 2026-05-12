import requests
import csv
from pathlib import Path

def main():
    apiKey = "Meraki API key goes here"
    wd = Path.cwd()
    csv_path = wd / "Meraki_LSP_Passwords.csv"

    # 1) Create CSV
    rows = [
        ["id", "name", "value"]
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Created {csv_path}")

    # 2) Read CSV
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        print("Contents:")
        for row in reader:
            print(row)

if __name__ == "__main__":
    main()