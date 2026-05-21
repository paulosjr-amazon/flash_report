#!/usr/bin/env python3
"""
Flash Report - Incident Indicators by Site
Weekly, YTD, Trend
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

CSV_FILE = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Dragonfly\incidents_raw.csv"
OUTPUT_FILE = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Dragonfly\output_incidents.csv"

FILTERS = {
    "Region": "ROW",
    "Country": "Brazil",
    "OBR BU": "LATAMCF",
    "OBR Org": "GCF",
}


def parse_float(val, default=0.0):
    try:
        return float(str(val).strip().replace(",", ""))
    except (ValueError, TypeError):
        return default


def parse_int(val, default=0):
    try:
        return int(float(str(val).strip().replace(",", "")))
    except (ValueError, TypeError):
        return default


def filter_row(row):
    for key, value in FILTERS.items():
        if row.get(key, "").strip().upper() != value.upper():
            return False
    return True


def calc_rate(count, hours):
    if hours <= 0:
        return 0.0
    return (count / hours) * 200000


def trend_str(current, previous):
    if previous == 0:
        return "NEW" if current > 0 else "-"
    diff = ((current - previous) / previous) * 100
    if diff > 0:
        return f"↑ {diff:.0f}%"
    elif diff < 0:
        return f"↓ {abs(diff):.0f}%"
    else:
        return "→ 0%"


def detect_delimiter(filepath):
    with open(filepath, "r", encoding="latin-1") as f:
        sample = f.read(2048)
    for delim in ["\t", ",", ";"]:
        if delim in sample:
            return delim
    return ","


def main():
    filepath = Path(CSV_FILE)
    if not filepath.exists():
        print(f"File not found: {CSV_FILE}")
        sys.exit(1)

    delimiter = detect_delimiter(filepath)

    # Read all rows
    rows = []
    with open(filepath, "r", encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            if filter_row(row):
                rows.append(row)

    if not rows:
        print("No data found after filtering.")
        return

    # Find latest week and previous week
    all_weeks = sorted(set(r.get("Fiscal Week", "").strip() for r in rows if r.get("Fiscal Week", "").strip()))
    if not all_weeks:
        print("No fiscal week data found.")
        return

    latest_week = all_weeks[-1]
    prev_week = all_weeks[-2] if len(all_weeks) >= 2 else None
    fiscal_year = rows[0].get("Fiscal Year", "").strip()

    print(f"  Latest week: {latest_week}")
    print(f"  Previous week: {prev_week}")
    print(f"  Fiscal year: {fiscal_year}")
    print()

    # Aggregate by site and week
    # Structure: site_data[site][week] = {hours, recordables, serious, dart, lt, msd, near_miss, all_inc, pit}
    site_data = defaultdict(lambda: defaultdict(lambda: {
        "hours": 0, "recordables": 0, "serious": 0, "dart": 0,
        "lt": 0, "msd": 0, "near_miss": 0, "all_inc": 0, "pit": 0,
        "top_hazards": []
    }))

    for row in rows:
        site = row.get("Site", "").strip()
        week = row.get("Fiscal Week", "").strip()
        if not site or not week:
            continue

        d = site_data[site][week]
        d["hours"] = parse_float(row.get("Total Hours"))  # Same per row per site/week
        d["recordables"] += parse_int(row.get("Recordable Incident Ind"))
        d["serious"] += parse_int(row.get("Serious Incident Ind"))
        d["dart"] += parse_int(row.get("DART Incident Ind"))
        d["lt"] += parse_int(row.get("Lost Time Incident Ind"))
        d["msd"] += parse_int(row.get("MSD Recordable Incident Ind"))
        d["near_miss"] += parse_int(row.get("Near Miss Incident Ind"))
        d["all_inc"] += parse_int(row.get("All Incident Ind"))
        d["pit"] += parse_int(row.get("PIT All Incident Ind"))
        hazard = row.get("Risk Hazard", "").strip()
        if hazard:
            d["top_hazards"].append(hazard)

    # Calculate YTD by site
    site_ytd = defaultdict(lambda: {"hours": 0, "recordables": 0, "serious": 0, "dart": 0, "lt": 0, "msd": 0, "all_inc": 0})
    for site, weeks in site_data.items():
        for week, d in weeks.items():
            site_ytd[site]["hours"] += d["hours"]
            site_ytd[site]["recordables"] += d["recordables"]
            site_ytd[site]["serious"] += d["serious"]
            site_ytd[site]["dart"] += d["dart"]
            site_ytd[site]["lt"] += d["lt"]
            site_ytd[site]["msd"] += d["msd"]
            site_ytd[site]["all_inc"] += d["all_inc"]

    # Build output
    results = []
    for site in sorted(site_data.keys()):
        curr = site_data[site].get(latest_week, {"hours": 0, "recordables": 0, "serious": 0, "dart": 0, "lt": 0, "msd": 0, "all_inc": 0, "near_miss": 0, "pit": 0, "top_hazards": []})
        prev = site_data[site].get(prev_week, {"hours": 0, "recordables": 0, "serious": 0, "dart": 0, "lt": 0, "msd": 0, "all_inc": 0, "near_miss": 0, "pit": 0, "top_hazards": []}) if prev_week else curr
        ytd = site_ytd[site]

        # Rates
        rir_week = calc_rate(curr["recordables"], curr["hours"])
        rir_prev = calc_rate(prev["recordables"], prev["hours"])
        rir_ytd = calc_rate(ytd["recordables"], ytd["hours"])

        sir_week = calc_rate(curr["serious"], curr["hours"])
        sir_prev = calc_rate(prev["serious"], prev["hours"])
        sir_ytd = calc_rate(ytd["serious"], ytd["hours"])

        dart_week = calc_rate(curr["dart"], curr["hours"])
        dart_prev = calc_rate(prev["dart"], prev["hours"])
        dart_ytd = calc_rate(ytd["dart"], ytd["hours"])

        ltir_week = calc_rate(curr["lt"], curr["hours"])
        ltir_prev = calc_rate(prev["lt"], prev["hours"])
        ltir_ytd = calc_rate(ytd["lt"], ytd["hours"])

        # Top hazard
        hazards = curr["top_hazards"]
        top_hazard = max(set(hazards), key=hazards.count) if hazards else "N/A"

        results.append({
            "Site": site,
            "Week": latest_week,
            "Hours": f"{curr['hours']:.0f}",
            "Incidents": curr["all_inc"],
            "Recordables": curr["recordables"],
            "Near_Misses": curr["near_miss"],
            "RIR_Week": f"{rir_week:.2f}",
            "RIR_YTD": f"{rir_ytd:.2f}",
            "RIR_Trend": trend_str(rir_week, rir_prev),
            "SIR_Week": f"{sir_week:.2f}",
            "SIR_YTD": f"{sir_ytd:.2f}",
            "SIR_Trend": trend_str(sir_week, sir_prev),
            "DART_Week": f"{dart_week:.2f}",
            "DART_YTD": f"{dart_ytd:.2f}",
            "DART_Trend": trend_str(dart_week, dart_prev),
            "LTIR_Week": f"{ltir_week:.2f}",
            "LTIR_YTD": f"{ltir_ytd:.2f}",
            "LTIR_Trend": trend_str(ltir_week, ltir_prev),
            "Top_Hazard": top_hazard,
        })
        print(f"  {site} - done")

    # Write output
    fieldnames = ["Site", "Week", "Hours", "Incidents", "Recordables", "Near_Misses",
                  "RIR_Week", "RIR_YTD", "RIR_Trend", "SIR_Week", "SIR_YTD", "SIR_Trend",
                  "DART_Week", "DART_YTD", "DART_Trend", "LTIR_Week", "LTIR_YTD", "LTIR_Trend",
                  "Top_Hazard"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"Done! {len(results)} sites.")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
