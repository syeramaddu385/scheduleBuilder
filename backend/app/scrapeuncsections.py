import time
import re
import requests
import pandas as pd

BASE_URL = "https://reports.unc.edu/class-search/"
TERM = "2026 Spring"  # <-- change this as needed
OUTPUT_FILE = "unc_all_sections_spring.csv"

subjects = ["AAAD", "ACSM", "ADJU", "AERO", "AFAM", "AFRI", "AHEC", "AHSC", "AIRS", "AMST", "ANA", "ANAT", "ANES", 
            "ANGL", "ANS", "ANSC", "ANTH", "APPL", "APSM", "ARA", "ARAB", "ARCH", "ARGE", "ARMY", "AROT", "ART", 
            "ARTH", "ARTS", "ASCI", "ASCM", "ASHV", "ASIA", "ASTR", "BACT", "BAE", "BBSP", "BCB", "BCH", "BCHM", 
            "BCS", "BEIJ", "BENG", "BERL", "BIOC", "BIOL", "BIOM", "BIOS", "BIOX", "BMA", "BME", "BMME", "BOE", 
            "BOIC", "BOLO", "BOT", "BOTN", "BRIS", "BSCI", "BUIS", "BULG", "BUSA", "BUSG", "BUSI", "BUSS", "CAPS", 
            "CATA", "CBAM", "CBIO", "CBMC", "CBPH", "CDFS", "CE", "CELT", "CENG", "CEOM", "CERT", "CGL", "CHE", 
            "CHEM", "CHER", "CHIN", "CHIP", "CHPM", "CHSC", "CITZ", "CLAR", "CLAS", "CLIC", "CLIT", "CLSC", "CLSK", 
            "CLST", "CMPL", "COML", "COMM", "COMP", "COPE", "CORE", "COSI", "CPXM", "CRMH", "CS", "CYTO", "CZCH", 
            "DATA", "DATE", "DDDD", "DECO", "DENG", "DENT", "DERM", "DESN", "DHED", "DHYG", "DNDG", "DNEC", "DNED", 
            "DPET", "DPMP", "DPOP", "DPPE", "DRAM", "DTCH", "DUAL", "EAST", "EC", "ECOL", "ECON", "ED", "ED1C", 
            "EDCI", "EDFO", "EDIN", "EDMX", "EDSP", "EDUC", "EDUX", "EE", "EENG", "EGR", "ELAW", "EMES", "ENDO", 
            "ENEC", "ENGL", "ENGM", "ENGR", "ENST", "ENT", "ENUR", "ENVR", "EPID", "ERMD", "EURO", "EXPR", "EXSS", 
            "EXTN", "FARE", "FES", "FMED", "FMME", "FOLK", "FOR", "FORE", "FORS", "FRED", "FREN", "FSCI", "GEN", 
            "GEOG", "GEOL", "GERJ", "GERM", "GHAN", "GLBE", "GLBL", "GN", "GNE", "GNET", "GOTT", "GOVT", "GRAD", 
            "GREK", "GSA", "GSLL", "HAD", "HADA", "HADM", "HAUS", "HBEH", "HBHE", "HCTS", "HDL", "HE", "HEBR", 
            "HECO", "HEED", "HIND", "HIST", "HLTH", "HMSC", "HMST", "HMTS", "HNRS", "HNUR", "HOME", "HORT", "HPAA", 
            "HPM", "HSCI", "HST", "HUNG", "HUSA", "HYGI", "IBMS", "ICMU", "ICRS", "ICSR", "IDST", "IENG", "IEP", 
            "IHMS", "IIOC", "IMMU", "INDC", "INDO", "INDR", "INFO", "INLS", "INTI", "INTS", "ISO", "ISRA", "ITAL", 
            "JAP", "JAPN", "JOMC", "JOUR", "JWST", "KANS", "KFM", "KOR", "LAQ", "LAR", "LARS", "LATN", "LAW", "LEED", 
            "LFIT", "LGLA", "LIBS", "LIMA", "LING", "LOND", "LSA", "LSEC", "LSRA", "LSSM", "LTAM", "LVE", "LW", "LYON", 
            "MA", "MAC", "MACD", "MACF", "MAE", "MAHP", "MANC", "MANS", "MASC", "MAT", "MATE", "MATH", "MAYA", "MBA", 
            "MBIO", "MCHL", "MCRO", "MDPH", "MDSP", "MEDC", "MEDF", "MEDI", "MEDT", "MEEN", "MEJO", "MENG", "MENH", 
            "MESE", "METR", "MEXI", "MHCH", "MIC", "MICR", "MILS", "MISC", "MNDG", "MNGT", "MODC", "MONT", "MONU", 
            "MOPH", "MOPL", "MPED", "MS", "MSBS", "MSCI", "MSMS", "MTEC", "MTSC", "MUSC", "MXCL", "MYCO", "NANZ", 
            "NAVS", "NBIO", "NDSS", "NE", "NENG", "NEUR", "NEUS", "NORW", "NSCI", "NSP", "NT", "NURS", "NUSJ", "NUTR", 
            "OBGN", "OBIO", "OCBM", "OCCT", "OCEN", "OCSC", "ODTP", "OMED", "OMSU", "OPER", "OPHT", "OR", "ORAD", "ORDI", 
            "ORLN", "ORPA", "ORSA", "ORSU", "ORTH", "ORTS", "OTOL", "P-LI", "PACE", "PADM", "PADS", "PALP", "PARA", 
            "PASC", "PATH", "PATY", "PEDI", "PEDO", "PEDS", "PERI", "PERS", "PERU", "PEW", "PHAD", "PHAR", "PHCG", 
            "PHCH", "PHCO", "PHCY", "PHED", "PHIL", "PHPR", "PHRS", "PHS", "PHTH", "PHYA", "PHYE", "PHYI", "PHYS", "PHYT", 
            "PHYY", "PLAN", "PLCY", "PLNT", "PLSH", "PLTM", "PMED", "PO", "POLI", "POLT", "PORT", "PP", "PPES", "PPOL", 
            "PPS", "PREV", "PROD", "PROS", "PRSN", "PS", "PSNU", "PSY", "PSYC", "PSYI", "PSYS", "PSYY", "PUBA", "PUBH", 
            "PUBP", "PUPA", "PVME", "PWAD", "PYSI", "QHCH", "RADG", "RADI", "RADY", "RECR", "REL", "RELI", "REST", "RFIX", 
            "RHAB", "RLGE", "ROMA", "ROML", "RPSY", "RTVM", "RUES", "RUMA", "RUSS", "SADM", "SANS", "SCLL", "SECR", "SERB", 
            "SEVI", "SIEN", "SLAV", "SNVR", "SOC", "SOCI", "SOCM", "SOIL", "SOMP", "SOWO", "SPAN", "SPCH", "SPCY", "SPHG", 
            "SPHS", "SSAP", "SSC", "SSCI", "ST", "STA", "STAN", "STAT", "STOR", "SUOP", "SURG", "SURS", "SURY", "SUSS", 
            "SWAH", "SWED", "TAML", "TEXT", "THER", "TOXC", "TOXI", "TREQ", "TRXN", "TUBI", "TURK", "UBDS", "UKRN", "UNI", 
            "UNIV", "URES", "VET", "VIET", "WGST", "WMST", "WOLL", "WOLO", "YIDI", "YORU", "ZOOL"]

HEADERS = {"User-Agent": "Mozilla/5.0"}


def normalize_instructor(raw: str) -> str:
    """
    Turn UNC instructor formats into something consistent for RMP joins.

    Handles:
    - "LAST,FIRST M" -> "First M Last"
    - multiple instructors split by / \ | ;
    """
    if raw is None:
        return ""
    raw = str(raw).strip()
    if not raw or raw.lower() == "none" or raw.lower() == "nan":
        return ""

    parts = re.split(r"\s*[\\/|;]\s*", raw)
    out = []

    for p in parts:
        p = p.strip()
        if not p or p.lower() in {"none", "nan"}:
            continue

        if "," in p:
            last, rest = p.split(",", 1)
            last = last.strip().title()
            rest = re.sub(r"\s+", " ", rest.strip())

            tokens = rest.split()
            suffixes = {"jr", "sr", "ii", "iii", "iv"}
            if tokens and tokens[-1].lower().strip(".") in suffixes:
                tokens = tokens[:-1]

            first = tokens[0].title() if tokens else ""
            middle = " ".join(t.title().rstrip(".") for t in tokens[1:]) if len(tokens) > 1 else ""
            name = f"{first} {middle} {last}".strip()
            name = re.sub(r"\s+", " ", name).strip()
            out.append(name)
        else:
            out.append(re.sub(r"\s+", " ", p).title())

    return " | ".join(out)


def fetch_subject_table(subject: str) -> pd.DataFrame | None:
    resp = requests.get(
        BASE_URL,
        headers=HEADERS,
        params={"subject": subject, "term": TERM},
        timeout=20,
    )

    if resp.status_code != 200:
        print(f"  ❌ {subject}: HTTP {resp.status_code}")
        return None

    # ✅ Catch the "No tables found" error HERE
    try:
        tables = pd.read_html(resp.text)
    except ValueError:
        print(f"  ⚠️ {subject}: No tables found (skipping)")
        return None

    if not tables:
        print(f"  ⚠️ {subject}: read_html returned no tables (skipping)")
        return None

    df = tables[0].copy()
    return df


def clean_df(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """
    Make output consistent and RMP-friendly.
    """
    # Add the subject we queried (useful as a stable key + debugging)
    df["Subject_Filter"] = subject

    # Standardize whitespace in all string-ish cells
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
            df[col] = df[col].replace({"nan": ""})

    # Preserve leading zeros / prevent Excel weirdness by forcing key columns to text
    text_cols = [
        "Class Section",
        "Catalog Num",
        "Class Number",
    ]
    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip().replace({"nan": ""})

    # Instructor join helpers
    if "Instructor" in df.columns:
        df["Instructor_Raw"] = df["Instructor"].fillna("").astype(str).str.strip()
        df["Instructor_Normalized"] = df["Instructor_Raw"].apply(normalize_instructor)
    else:
        df["Instructor_Raw"] = ""
        df["Instructor_Normalized"] = ""

    # Optional: a stable course key that’s super useful for your schedule builder
    if "Subject" in df.columns and "Catalog Num" in df.columns:
        df["CourseKey"] = (df["Subject"].astype(str).str.strip() + " " + df["Catalog Num"].astype(str).str.strip()).str.strip()
    elif "Catalog Num" in df.columns:
        df["CourseKey"] = (subject + " " + df["Catalog Num"].astype(str).str.strip()).str.strip()
    else:
        df["CourseKey"] = subject

    return df


def main():
    all_frames: list[pd.DataFrame] = []

    for subject in subjects:
        print(f"Scraping {subject} ({TERM})...")

        df = fetch_subject_table(subject)
        if df is None or df.empty:
            print(f"  ⚠️ {subject}: empty")
            continue

        df = clean_df(df, subject)
        all_frames.append(df)

        print(f"{subject}: {len(df)} rows")
        time.sleep(0.8)

    if not all_frames:
        print("No data collected.")
        return

    final = pd.concat(all_frames, ignore_index=True)

    # Write CSV. quoting is handled by pandas; commas/newlines in fields won’t break columns.
    final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Done. CSV saved as: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
