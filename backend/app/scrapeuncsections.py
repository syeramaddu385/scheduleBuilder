import requests
import csv
import time
from bs4 import BeautifulSoup

BASE_URL = "https://reports.unc.edu/class-search/?subject={}"

subjects = [
    "AAAD","ACSM","ADJU","AERO","AFAM","AFRI","AHEC","AHSC","AIRS","AMST",
    "ANA","ANAT","ANES","ANGL","ANS","ANSC","ANTH","APPL","APSM","ARA",
    # (keep your full list exactly as you have it)
    "MATH","STOR","PHYS","COMP"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

OUTPUT_FILE = "unc_all_sections.csv"

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    header_written = False

    for subject in subjects:
        url = BASE_URL.format(subject)
        print(f"Scraping {subject}...")

        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"  ❌ Failed ({response.status_code})")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table")
        if not table:
            print(f"  ⚠️ No table found")
            continue

        # Extract headers once
        if not header_written:
            headers = [
                th.get_text(strip=True)
                for th in table.find_all("th")
            ]
            writer.writerow(headers)
            header_written = True

        # Extract rows
        rows = table.find_all("tr")[1:]  # skip header row
        for row in rows:
            cells = [
                td.get_text(strip=True)
                for td in row.find_all("td")
            ]
            if cells:
                writer.writerow(cells)

        print(f"  ✅ {len(rows)} sections saved")
        time.sleep(0.5)  # be polite to UNC servers

print("🎉 Done. CSV saved as:", OUTPUT_FILE)
