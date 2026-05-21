#!/usr/bin/env python3
"""
Flash Report Unificado - Um CSV, colunas por assunto
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict
from deep_translator import GoogleTranslator

# --- Paths ---
DRAGONFLY_CSV = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Dragonfly\dragonfly_raw.csv"
INCIDENTS_CSV = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Incident\incidents_raw.csv"
OUTPUT_FILE = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Output\output_flash_report.csv"

ALLOWED_BUS = ["AMZL-LATAM", "LATAMCF", "ATS-LATAM"]

COORDINATES = {
    "GRU10": (-23.5505, -46.6333), "DBH5": (-19.9200, -43.9400),
    "DBS5": (-15.8700, -47.9800), "DBS7": (-15.8500, -47.9600),
    "DBZ1": (-23.3350, -46.8550), "DCE3": (-3.7900, -38.5100),
    "DCE5": (-3.8000, -38.5200), "DCP5": (-22.9099, -47.0626),
    "DES2": (-20.2076, -40.2286), "DGO2": (-16.6869, -49.2648),
    "DMG2": (-19.9300, -44.0500), "DPB3": (-7.1195, -34.8450),
    "DPE2": (-8.0500, -34.8700), "DPE4": (-8.0600, -34.8800),
    "DPR2": (-25.4300, -49.2700), "DRJ3": (-22.7800, -43.3100),
    "DRJ5": (-22.8700, -43.3500), "DRS5": (-29.9700, -51.1800),
    "DSA8": (-12.7000, -38.3300), "DSCA": (-27.5954, -48.5480),
    "DSP2": (-23.5230, -46.6920), "DSP3": (-23.5500, -46.6350),
    "DSP5": (-23.4500, -46.5300), "DSP6": (-23.5600, -46.7100),
    "DSP7": (-23.5100, -46.6500), "SRP9": (-5.7945, -35.2110),
    "BSB1": (-15.9836, -47.9879), "CNF1": (-19.9439, -44.1076),
    "CNF2": (-19.7664, -44.0871), "CNF5": (-22.7839, -46.2324),
    "CWB1": (-25.5315, -49.1756), "FOR2": (-3.8671, -38.5119),
    "FOR3": (-3.8782, -38.5004), "GIG1": (-22.8002, -43.3513),
    "GIG2": (-22.7715, -43.3994), "GRU5": (-23.3305, -46.8506),
    "GRU6": (-23.3494, -46.8745), "GRU8": (-23.3494, -46.8745),
    "GRU9": (-23.3565, -46.8769), "POA1": (-29.8534, -51.2486),
    "REC1": (-8.2253, -34.9936), "REC3": (-8.2868, -35.0387),
    "SSA5": (-12.6996, -38.3263), "VIX1": (-20.2076, -40.2286),
    "XBS1": (-15.7797, -47.9297), "XCV9": (-23.3565, -46.8769),
    "XBRA": (-23.3400, -46.8600), "XBRB": (-8.2600, -35.0200),
    "XBRC": (-12.7000, -38.3300), "XBRT": (-23.3400, -46.8600),
    "XBRZ": (-23.3400, -46.8600), "VBS1": (-15.9836, -47.9879),
    "VDF1": (-15.9836, -47.9879), "CGH3": (-23.3400, -46.8600),
    "CGH7": (-23.5000, -46.7500), "CNF7": (-19.9300, -44.0500),
    "GIG7": (-22.8000, -43.3500), "REC9": (-8.0500, -34.8700),
    "VBAN": (-26.3045, -48.8487), "VBEM": (-12.9714, -38.5124),
    "VBPA": (-23.5870, -46.6560), "VBSA": (-19.9200, -43.9400),
    "XBA1": (-12.2669, -38.9666), "XCP1": (-22.9099, -47.0626),
    "XPB1": (-7.2306, -35.8811), "XRJ2": (-22.8833, -43.1036),
    "XRJ3": (-22.7856, -43.3117), "XRJ4": (-22.5112, -43.1779),
    "XSJ1": (-23.3050, -45.9660), "XSP2": (-23.4500, -46.5300),
    "XSP3": (-23.6700, -46.4600), "XSP4": (-23.5505, -46.6333),
    "XSP7": (-23.1857, -46.8978), "XSP9": (-22.7338, -47.6476),
}

WEIGHTS = {"severity": 0.30, "quality_response": 0.25, "sentiment": 0.20, "first_time": 0.15, "description_length": 0.10}
translator = GoogleTranslator(source="pt", target="en")


def parse_float(val, default=0.0):
    try:
        return float(str(val).strip().replace(",", ""))
    except (ValueError, TypeError):
        return default


def calc_rate(count, hours):
    return (count / hours) * 200000 if hours > 0 else 0.0


def trend_str(current, previous):
    if previous == 0:
        return "NEW" if current > 0 else "-"
    diff = ((current - previous) / previous) * 100
    if diff > 0:
        return f"up {diff:.0f}%"
    elif diff < 0:
        return f"down {abs(diff):.0f}%"
    return "flat"


def truncate_description(text, max_len=300):
    text = text.strip().replace("\
", " ").replace("\r", " ")
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def translate_text(text):
    try:
        return translator.translate(text)
    except:
        return text


def format_date(date_str):
    return date_str.strip().split(" ")[0] if date_str else "N/A"


def detect_delimiter(filepath):
    with open(filepath, "r", encoding="latin-1") as f:
        sample = f.read(2048)
    for delim in ["\t", ",", ";"]:
        if delim in sample:
            return delim
    return ","


def is_positive_sentiment(sentiment):
    if not sentiment:
        return False
    return any(k in sentiment.strip().lower() for k in ["proactive", "constructive", "positive", "suggestion"])


def compute_score(row):
    severity_score = min(parse_float(row.get("Severity (AI)")) / 5.0, 1.0)
    qri_score = min(parse_float(row.get("Quality Response Indicator (AI)")) / 5.0, 1.0)
    sentiment_text = row.get("Sentiment (AI)", "") or row.get("Sentiment Description (AI)", "")
    sentiment_score = 1.0 if is_positive_sentiment(sentiment_text) else 0.0
    first_time = str(row.get("Is First Time Submitter", "")).strip().lower()
    first_time_score = 1.0 if first_time in ("yes", "true", "1") else 0.0
    desc_score = min(len(row.get("Safety Observation", "") or "") / 100.0, 1.0)
    score = (WEIGHTS["severity"] * severity_score + WEIGHTS["quality_response"] * qri_score +
             WEIGHTS["sentiment"] * sentiment_score + WEIGHTS["first_time"] * first_time_score +
             WEIGHTS["description_length"] * desc_score)
    return score, first_time_score


# ============================================================
# MAIN
# ============================================================
def main():
    # --- INCIDENTS ---
    print("Processing Incidents...")
    inc_path = Path(INCIDENTS_CSV)
    inc_rows = []
    if inc_path.exists():
        with open(inc_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Region", "").strip().upper() != "ROW":
                    continue
                if row.get("Country", "").strip().upper() != "BR":
                    continue
                if row.get("OBR BU", "").strip().upper() not in [b.upper() for b in ALLOWED_BUS]:
                    continue
                inc_rows.append(row)

    all_weeks = sorted(set(r.get("Year-Week", "").strip() for r in inc_rows if r.get("Year-Week", "").strip()))
    latest_week = all_weeks[-1] if all_weeks else ""
    prev_week = all_weeks[-2] if len(all_weeks) >= 2 else None

    # Aggregate incidents by site/week
    site_inc = defaultdict(lambda: defaultdict(lambda: {"hours": 0, "ri": 0, "si": 0, "dart": 0, "lti": 0, "all_inc": 0, "near_miss": 0}))
    site_meta = {}

    for row in inc_rows:
        site = row.get("Site", "").strip()
        week = row.get("Year-Week", "").strip()
        if not site or not week:
            continue
        d = site_inc[site][week]
        d["hours"] += parse_float(row.get("Total Hours"))
        d["ri"] += parse_float(row.get("RI Count"))
        d["si"] += parse_float(row.get("SI Count"))
        d["dart"] += parse_float(row.get("DART Count"))
        d["lti"] += parse_float(row.get("LTI Count"))
        d["all_inc"] += parse_float(row.get("All Incident Count"))
        d["near_miss"] += parse_float(row.get("Near Miss Count"))
        if site not in site_meta:
            site_meta[site] = {
                "BU": row.get("OBR BU", "").strip(),
                "Year": row.get("Fiscal Year", "").strip(),
                "Quarter": row.get("Year-Quarter", "").strip(),
                "Month": row.get("Year-Month", "").strip(),
            }

    # YTD
    site_ytd = defaultdict(lambda: {"hours": 0, "ri": 0, "si": 0, "dart": 0, "lti": 0})
    for site, weeks in site_inc.items():
        for week, d in weeks.items():
            site_ytd[site]["hours"] += d["hours"]
            site_ytd[site]["ri"] += d["ri"]
            site_ytd[site]["si"] += d["si"]
            site_ytd[site]["dart"] += d["dart"]
            site_ytd[site]["lti"] += d["lti"]

    # --- DRAGONFLY ---
    print("Processing Dragonfly...")
    dfy_path = Path(DRAGONFLY_CSV)
    dfy_candidates = []
    if dfy_path.exists():
        delimiter = detect_delimiter(dfy_path)
        with open(dfy_path, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                if row.get("Region", "").strip().upper() != "ROW":
                    continue
                if row.get("Country", "").strip().upper() != "BRAZIL":
                    continue
                if row.get("OBR BU", "").strip().upper() != "LATAMCF":
                    continue
                if row.get("OBR Org", "").strip().upper() != "GCF":
                    continue
                login = row.get("Submitter Login", "").strip()
                if not login or login.lower() in ("anonymous", "anon", ""):
                    continue
                score, first_time = compute_score(row)
                dfy_candidates.append((score, first_time, row))

    dfy_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # Best dragonfly per site
    dfy_by_site = {}
    blue_badge_sites = ["GRU5", "GRU8", "GRU9", "CNF1"]
    for score, first_time, row in dfy_candidates:
        site = row.get("Site", "N/A").strip()
        if site.upper() in dfy_by_site:
            continue
        desc = truncate_description(row.get("Safety Observation", ""))
        desc_en = translate_text(desc)
        login = row.get("Submitter Login", "N/A").strip()
        hist_count = sum(1 for _, _, r in dfy_candidates if r.get("Submitter Login", "").strip() == login)
        shoutout = ""
        if site.upper() in blue_badge_sites:
            shoutout = "\
\
💪 Above and beyond! Recognize them: https://atoz.amazon.work/shout-outs\
"
        full_desc = f"📦 {site}       👤 @{login}       ✍️ {hist_count} obs.\
\
{desc_en}{shoutout}"
        date = format_date(row.get("Finding Creation Timestamp (UTC)", ""))
        dfy_by_site[site.upper()] = {"DFY_Description": full_desc, "DFY_Date": date}
        print(f"  DFY {site} - done")

    # --- BUILD UNIFIED OUTPUT ---
    print("\
Building unified output...")
    all_sites = sorted(set(list(site_inc.keys()) + [s for s in dfy_by_site.keys()]))
    empty_inc = {"hours": 0, "ri": 0, "si": 0, "dart": 0, "lti": 0, "all_inc": 0, "near_miss": 0}

    results = []
    for site in all_sites:
        meta = site_meta.get(site, {"BU": "", "Year": "", "Quarter": "", "Month": ""})
        lat, lon = COORDINATES.get(site.upper(), ("", ""))

        curr = site_inc[site].get(latest_week, empty_inc)
        prev = site_inc[site].get(prev_week, empty_inc) if prev_week else curr
        ytd = site_ytd[site]

        rir_week = calc_rate(curr["ri"], curr["hours"])
        rir_prev = calc_rate(prev["ri"], prev["hours"])
        rir_ytd = calc_rate(ytd["ri"], ytd["hours"])
        sir_week = calc_rate(curr["si"], curr["hours"])
        sir_prev = calc_rate(prev["si"], prev["hours"])
        sir_ytd = calc_rate(ytd["si"], ytd["hours"])
        dart_week = calc_rate(curr["dart"], curr["hours"])
        dart_prev = calc_rate(prev["dart"], prev["hours"])
        dart_ytd = calc_rate(ytd["dart"], ytd["hours"])
        ltir_week = calc_rate(curr["lti"], curr["hours"])
        ltir_prev = calc_rate(prev["lti"], prev["hours"])
        ltir_ytd = calc_rate(ytd["lti"], ytd["hours"])

        dfy = dfy_by_site.get(site.upper(), {"DFY_Description": "", "DFY_Date": ""})

        results.append({
            "Site": site,
            "BU": meta["BU"],
            "Latitude": lat,
            "Longitude": lon,
            "Total_Hours": f"{curr['hours']:.0f}",
            "Year": meta["Year"],
            "Quarter": meta["Quarter"],
            "Month": meta["Month"],
            "Week": latest_week,
            "INC_Incidents": f"{curr['all_inc']:.0f}",
            "INC_Recordables": f"{curr['ri']:.0f}",
            "INC_Near_Misses": f"{curr['near_miss']:.0f}",
            "INC_RIR_Week": f"{rir_week:.2f}",
            "INC_RIR_YTD": f"{rir_ytd:.2f}",
            "INC_RIR_Trend": trend_str(rir_week, rir_prev),
            "INC_SIR_Week": f"{sir_week:.2f}",
            "INC_SIR_YTD": f"{sir_ytd:.2f}",
            "INC_SIR_Trend": trend_str(sir_week, sir_prev),
            "INC_DART_Week": f"{dart_week:.2f}",
            "INC_DART_YTD": f"{dart_ytd:.2f}",
            "INC_DART_Trend": trend_str(dart_week, dart_prev),
            "INC_LTIR_Week": f"{ltir_week:.2f}",
            "INC_LTIR_YTD": f"{ltir_ytd:.2f}",
            "INC_LTIR_Trend": trend_str(ltir_week, ltir_prev),
            "DFY_Description": dfy["DFY_Description"],
            "DFY_Date": dfy["DFY_Date"],
        })
        print(f"  {site} - done")

    # Write
    fieldnames = ["Site", "BU", "Latitude", "Longitude", "Total_Hours", "Year", "Quarter", "Month", "Week",
                  "INC_Incidents", "INC_Recordables", "INC_Near_Misses",
                  "INC_RIR_Week", "INC_RIR_YTD", "INC_RIR_Trend",
                  "INC_SIR_Week", "INC_SIR_YTD", "INC_SIR_Trend",
                  "INC_DART_Week", "INC_DART_YTD", "INC_DART_Trend",
                  "INC_LTIR_Week", "INC_LTIR_YTD", "INC_LTIR_Trend",
                  "DFY_Description", "DFY_Date"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\
Done! {len(results)} rows.")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
