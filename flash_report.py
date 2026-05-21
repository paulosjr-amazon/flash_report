#!/usr/bin/env python3
"""
Flash Report Unificado — Incidents + Dragonfly + Inspections
Output: output_flash_report.csv
"""

import csv
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

try:
    from deep_translator import GoogleTranslator
    _translator = GoogleTranslator(source="pt", target="en")
    def translate_text(text):
        try:
            return _translator.translate(text) if text else text
        except Exception:
            return text
except ImportError:
    def translate_text(text):
        return text

# ── Paths ─────────────────────────────────────────────────────────────────────
INCIDENTS_CSV   = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Incident\Incidents.csv"
DRAGONFLY_CSV   = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Dragonfly\Dragonfly.csv"
INSPECTIONS_CSV = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Update\Inspections\Inspections.csv"
MANUAL_CSV      = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Python\manual_input.csv"
OUTPUT_CSV      = r"C:\Users\paulosjr\OneDrive - amazon.com\Database\Python\output_flash_report.csv"

# ── Input column names (adjust if source headers change) ──────────────────────
INC = {
    "site": "Site", "bu": "OBR BU", "sub_bu": "OBR Sub BU",
    "week": "Year-Week", "month": "Year-Month", "quarter": "Year-Quarter", "year": "Fiscal Year",
    "region": "Region", "country": "Country",
    "hours": "Total Hours",
    "all_inc": "All Incident Count", "si": "SI Count", "ri": "RI Count",
    "dart": "DART Count", "lti": "LTI Count", "fai": "FAI Count",
    "msd_ri": "MSD RI Count", "msd_lti": "MSD LTI Count",
    "near_miss": "Near Miss Count",
    "pit_all": "PIT All Count", "pit_si": "PIT SI Count", "pit_ri": "PIT RI Count",
    "yard": "Yard Count", "pit_ped": "PIT Pedestrian Count",
}

DFY = {
    "site": "Site", "bu": "OBR BU", "org": "OBR Org",
    "week": "Year-Week",          # if absent, derived from created_at
    "region": "Region", "country": "Country",
    "login": "Submitter Login",
    "observation": "Safety Observation",
    "severity": "Severity (AI)",
    "qri": "Quality Response Indicator (AI)",
    "sentiment": "Sentiment (AI)",
    "sentiment_desc": "Sentiment Description (AI)",
    "first_time": "Is First Time Submitter",
    "status": "Finding Status",   # "Closed" / "Open"
    "has_feedback": "Has Feedback",
    "days_completion": "Days to Completion",
    "days_response": "Days to Response",
    "created_at": "Finding Creation Timestamp (UTC)",
}

INSP = {
    "site": "Site", "week": "Year-Week",
    "due_insp": "Due Inspections", "otc_insp": "Completed Inspections",
    "due_tasks": "Due Tasks", "otc_tasks": "Completed Tasks",
    "on_time": "On Time Inspections", "overdue": "Overdue Inspections",
    "tasks_on_time": "On Time Tasks", "tasks_overdue": "Overdue Tasks",
}

ALLOWED_BUS = {"AMZL-LATAM", "LATAMCF", "ATS-LATAM"}
DFY_FILTERS = {"Region": "ROW", "Country": "Brazil", "OBR BU": "LATAMCF", "OBR Org": "GCF"}
BLUE_BADGE_SITES = {"GRU5", "GRU8", "GRU9", "CNF1"}

DFY_SCORE_WEIGHTS = {
    "severity": 0.30, "quality_response": 0.25, "sentiment": 0.20,
    "first_time": 0.15, "description_length": 0.10,
}

COORDINATES = {
    "GRU10": (-23.5505,-46.6333), "DBH5": (-19.9200,-43.9400), "DBS5": (-15.8700,-47.9800),
    "DBS7": (-15.8500,-47.9600), "DBZ1": (-23.3350,-46.8550), "DCE3": (-3.7900,-38.5100),
    "DCE5": (-3.8000,-38.5200), "DCP5": (-22.9099,-47.0626), "DES2": (-20.2076,-40.2286),
    "DGO2": (-16.6869,-49.2648), "DMG2": (-19.9300,-44.0500), "DPB3": (-7.1195,-34.8450),
    "DPE2": (-8.0500,-34.8700), "DPE4": (-8.0600,-34.8800), "DPR2": (-25.4300,-49.2700),
    "DRJ3": (-22.7800,-43.3100), "DRJ5": (-22.8700,-43.3500), "DRS5": (-29.9700,-51.1800),
    "DSA8": (-12.7000,-38.3300), "DSCA": (-27.5954,-48.5480), "DSP2": (-23.5230,-46.6920),
    "DSP3": (-23.5500,-46.6350), "DSP5": (-23.4500,-46.5300), "DSP6": (-23.5600,-46.7100),
    "DSP7": (-23.5100,-46.6500), "SRP9": (-5.7945,-35.2110), "BSB1": (-15.9836,-47.9879),
    "CNF1": (-19.9439,-44.1076), "CNF2": (-19.7664,-44.0871), "CNF5": (-22.7839,-46.2324),
    "CWB1": (-25.5315,-49.1756), "FOR2": (-3.8671,-38.5119), "FOR3": (-3.8782,-38.5004),
    "GIG1": (-22.8002,-43.3513), "GIG2": (-22.7715,-43.3994), "GRU5": (-23.3305,-46.8506),
    "GRU6": (-23.3494,-46.8745), "GRU8": (-23.3494,-46.8745), "GRU9": (-23.3565,-46.8769),
    "POA1": (-29.8534,-51.2486), "REC1": (-8.2253,-34.9936), "REC3": (-8.2868,-35.0387),
    "SSA5": (-12.6996,-38.3263), "VIX1": (-20.2076,-40.2286), "XBS1": (-15.7797,-47.9297),
    "XCV9": (-23.3565,-46.8769), "XBRA": (-23.3400,-46.8600), "XBRB": (-8.2600,-35.0200),
    "XBRC": (-12.7000,-38.3300), "XBRT": (-23.3400,-46.8600), "XBRZ": (-23.3400,-46.8600),
    "VBS1": (-15.9836,-47.9879), "VDF1": (-15.9836,-47.9879), "CGH3": (-23.3400,-46.8600),
    "CGH7": (-23.5000,-46.7500), "CNF7": (-19.9300,-44.0500), "GIG7": (-22.8000,-43.3500),
    "REC9": (-8.0500,-34.8700), "VBAN": (-26.3045,-48.8487), "VBEM": (-12.9714,-38.5124),
    "VBPA": (-23.5870,-46.6560), "VBSA": (-19.9200,-43.9400), "XBA1": (-12.2669,-38.9666),
    "XCP1": (-22.9099,-47.0626), "XPB1": (-7.2306,-35.8811), "XRJ2": (-22.8833,-43.1036),
    "XRJ3": (-22.7856,-43.3117), "XRJ4": (-22.5112,-43.1779), "XSJ1": (-23.3050,-45.9660),
    "XSP2": (-23.4500,-46.5300), "XSP3": (-23.6700,-46.4600), "XSP4": (-23.5505,-46.6333),
    "XSP7": (-23.1857,-46.8978), "XSP9": (-22.7338,-47.6476),
    "DAM1": (-3.1190,-60.0217), "DBR9": (-12.9714,-38.5124), "DFR2": (-10.9000,-37.0500),
    "DPE4": (-8.0600,-34.8800), "DRJ5": (-22.8700,-43.3500), "ECB8": (-12.9714,-38.5124),
    "EGO8": (-16.6869,-49.2648), "ELP8": (-10.9000,-37.0500), "EMG8": (-19.9200,-43.9400),
    "EPE8": (-8.0600,-34.8800), "EQU8": (-4.2700,-38.9000), "ERS8": (-29.9700,-51.1800),
    "ESA8": (-12.9714,-38.5124), "ESB8": (-12.9714,-38.5124), "ESE8": (-20.2076,-40.2286),
    "ESS8": (-12.9714,-38.5124), "EUA8": (-23.5505,-46.6333), "EVT8": (-20.3222,-40.3381),
    "VBJ1": (-23.3050,-45.9660), "VBM1": (-19.9200,-43.9400), "VBM2": (-19.9200,-43.9400),
}

OUTPUT_FIELDS = [
    "Site", "BU", "Sub_BU", "Latitude", "Longitude",
    "Total_Hours_Week", "Total_Hours_YTD",
    "Year", "Quarter", "Month", "Week",
    "INC_All_Week", "INC_All_YTD", "INC_SI_Week", "INC_SI_YTD",
    "INC_RI_Week", "INC_RI_YTD", "INC_DART_Week", "INC_DART_YTD",
    "INC_LTI_Week", "INC_LTI_YTD", "INC_FAI_Week", "INC_FAI_YTD",
    "INC_MSD_RI_Week", "INC_MSD_RI_YTD", "INC_MSD_LTI_Week",
    "INC_Near_Miss_Week", "INC_Near_Miss_YTD",
    "INC_PIT_All_Week", "INC_PIT_SI_Week", "INC_PIT_RI_Week",
    "INC_Yard_Week", "INC_PIT_Ped_Week",
    "INC_RIR_Week", "INC_RIR_YTD", "INC_SIR_Week", "INC_SIR_YTD",
    "INC_DART_Rate_Week", "INC_DART_Rate_YTD", "INC_LTIR_Week", "INC_LTIR_YTD",
    "INC_MSD_RIR_Week", "INC_MSD_RIR_YTD", "INC_FAIR_Week", "INC_FAIR_YTD",
    "INSP_Due_Inspections", "INSP_Inspection_OTC", "INSP_Due_Tasks", "INSP_Task_OTC",
    "INSP_On_Time", "INSP_Overdue", "INSP_Tasks_On_Time", "INSP_Tasks_Overdue",
    "DFY_Total_Obs_Week", "DFY_Total_Obs_YTD", "DFY_Closed_Week", "DFY_Closed_YTD",
    "DFY_Open_Week", "DFY_Open_YTD", "DFY_Closure_Rate_Week", "DFY_Closure_Rate_YTD",
    "DFY_Feedback_Rate_Week", "DFY_Feedback_Rate_YTD",
    "DFY_First_Timers_Week", "DFY_First_Timers_YTD",
    "DFY_Sentiment_Positive_Pct_Week", "DFY_Sentiment_Positive_Pct_YTD",
    "DFY_QRI_Avg_Week", "DFY_QRI_Avg_YTD",
    "DFY_Days_Completion_Avg_Week", "DFY_Days_Completion_Avg_YTD",
    "DFY_Days_Response_Avg_Week", "DFY_Days_Response_Avg_YTD",
    "DFY_Rate_Week", "DFY_Rate_YTD",
    "DFY_Submitter_Rate_Week", "DFY_Submitter_Rate_YTD",
    "DFY_Description", "DFY_Date",
    "INSP_Due_Insp_Week", "INSP_Due_Insp_YTD", "INSP_OTC_Week", "INSP_OTC_YTD",
    "INSP_Due_Tasks_Week", "INSP_Due_Tasks_YTD", "INSP_Task_OTC_Week", "INSP_Task_OTC_YTD",
    "INSP_On_Time_Week", "INSP_On_Time_YTD", "INSP_Overdue_Week", "INSP_Overdue_YTD",
    "INSP_Tasks_On_Time_Week", "INSP_Tasks_On_Time_YTD",
    "INSP_Tasks_Overdue_Week", "INSP_Tasks_Overdue_YTD",
    "Manual_Success_Story", "Manual_Tip", "Manual_Submitted_By",
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def pf(val, default=0.0):
    try:
        return float(str(val).strip().replace(",", ""))
    except (ValueError, TypeError):
        return default


def pi(val, default=0):
    try:
        return int(float(str(val).strip().replace(",", "")))
    except (ValueError, TypeError):
        return default


def rate(count, hours):
    return round((count / hours) * 200000, 2) if hours > 0 else 0.0


def pct(num, den):
    return round((num / den) * 100, 1) if den > 0 else 0.0


def avg(total, count):
    return round(total / count, 2) if count > 0 else 0.0


def fmt(val):
    return f"{val:.2f}" if isinstance(val, float) else str(val)


def detect_delimiter(filepath):
    with open(filepath, "r", encoding="latin-1") as f:
        sample = f.read(4096)
    for d in ["\t", ";", ","]:
        if d in sample:
            return d
    return ","


def read_csv(filepath, encoding="utf-8-sig"):
    p = Path(filepath)
    if not p.exists():
        print(f"  [SKIP] Not found: {filepath}")
        return []
    enc = encoding
    delim = detect_delimiter(p)
    try:
        with open(p, "r", encoding=enc) as f:
            return list(csv.DictReader(f, delimiter=delim))
    except UnicodeDecodeError:
        with open(p, "r", encoding="latin-1") as f:
            return list(csv.DictReader(f, delimiter=delim))


def timestamp_to_week(ts):
    if not ts:
        return ""
    ts = ts.strip()
    for fmt_str in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(ts.split(".")[0], fmt_str)
            y, w, _ = dt.isocalendar()
            return f"{y}-W{w:02d}"
        except ValueError:
            continue
    return ""


def is_positive_sentiment(text):
    if not text:
        return False
    return any(k in text.lower() for k in ["proactive", "constructive", "positive", "suggestion"])


def dfy_score(row):
    sev = min(pf(row.get(DFY["severity"])) / 5.0, 1.0)
    qri = min(pf(row.get(DFY["qri"])) / 5.0, 1.0)
    sent = row.get(DFY["sentiment"], "") or row.get(DFY["sentiment_desc"], "")
    sent_s = 1.0 if is_positive_sentiment(sent) else 0.0
    ft = str(row.get(DFY["first_time"], "")).strip().lower()
    ft_s = 1.0 if ft in ("yes", "true", "1") else 0.0
    desc_s = min(len(row.get(DFY["observation"], "") or "") / 100.0, 1.0)
    score = (DFY_SCORE_WEIGHTS["severity"] * sev +
             DFY_SCORE_WEIGHTS["quality_response"] * qri +
             DFY_SCORE_WEIGHTS["sentiment"] * sent_s +
             DFY_SCORE_WEIGHTS["first_time"] * ft_s +
             DFY_SCORE_WEIGHTS["description_length"] * desc_s)
    return score, ft_s


def truncate(text, n=300):
    text = (text or "").strip().replace("\n", " ").replace("\r", " ")
    return text if len(text) <= n else text[:n - 3] + "..."


# ── Load & aggregate Incidents ────────────────────────────────────────────────
def load_incidents():
    rows = read_csv(INCIDENTS_CSV)
    filtered = []
    for r in rows:
        if r.get(INC["region"], "").strip().upper() != "ROW":
            continue
        if r.get(INC["country"], "").strip().upper() != "BR":
            continue
        if r.get(INC["bu"], "").strip().upper() not in {b.upper() for b in ALLOWED_BUS}:
            continue
        filtered.append(r)
    print(f"  Incidents: {len(filtered)} rows after filter")

    all_weeks = sorted({r.get(INC["week"], "").strip() for r in filtered if r.get(INC["week"], "").strip()})
    latest = all_weeks[-1] if all_weeks else ""
    prev = all_weeks[-2] if len(all_weeks) >= 2 else ""
    print(f"  Latest week: {latest} | Prev: {prev}")

    zero = lambda: {k: 0.0 for k in ["hours","all","si","ri","dart","lti","fai","msd_ri","msd_lti","near_miss","pit_all","pit_si","pit_ri","yard","pit_ped"]}
    site_week = defaultdict(lambda: defaultdict(zero))
    site_meta = {}

    for r in filtered:
        site = r.get(INC["site"], "").strip()
        week = r.get(INC["week"], "").strip()
        if not site or not week:
            continue
        d = site_week[site][week]
        d["hours"]    += pf(r.get(INC["hours"]))
        d["all"]      += pf(r.get(INC["all_inc"]))
        d["si"]       += pf(r.get(INC["si"]))
        d["ri"]       += pf(r.get(INC["ri"]))
        d["dart"]     += pf(r.get(INC["dart"]))
        d["lti"]      += pf(r.get(INC["lti"]))
        d["fai"]      += pf(r.get(INC["fai"]))
        d["msd_ri"]   += pf(r.get(INC["msd_ri"]))
        d["msd_lti"]  += pf(r.get(INC["msd_lti"]))
        d["near_miss"]+= pf(r.get(INC["near_miss"]))
        d["pit_all"]  += pf(r.get(INC["pit_all"]))
        d["pit_si"]   += pf(r.get(INC["pit_si"]))
        d["pit_ri"]   += pf(r.get(INC["pit_ri"]))
        d["yard"]     += pf(r.get(INC["yard"]))
        d["pit_ped"]  += pf(r.get(INC["pit_ped"]))
        if site not in site_meta:
            site_meta[site] = {
                "bu": r.get(INC["bu"], "").strip(),
                "sub_bu": r.get(INC["sub_bu"], "").strip(),
                "year": r.get(INC["year"], "").strip(),
                "quarter": r.get(INC["quarter"], "").strip(),
                "month": r.get(INC["month"], "").strip(),
            }

    # YTD per site
    site_ytd = defaultdict(zero)
    for site, weeks in site_week.items():
        for d in weeks.values():
            for k in site_ytd[site]:
                site_ytd[site][k] += d[k]

    return site_week, site_ytd, site_meta, latest, prev


# ── Load & aggregate Dragonfly ─────────────────────────────────────────────────
def load_dragonfly(latest_week):
    rows = read_csv(DRAGONFLY_CSV, encoding="latin-1")
    filtered = []
    for r in rows:
        if r.get(DFY["region"], "").strip().upper() != DFY_FILTERS["Region"].upper():
            continue
        if r.get(DFY["country"], "").strip().upper() != DFY_FILTERS["Country"].upper():
            continue
        if r.get(DFY["bu"], "").strip().upper() != DFY_FILTERS["OBR BU"].upper():
            continue
        if r.get(DFY["org"], "").strip().upper() != DFY_FILTERS["OBR Org"].upper():
            continue
        login = r.get(DFY["login"], "").strip()
        if not login or login.lower() in ("anonymous", "anon", ""):
            continue
        # Resolve week
        w = r.get(DFY["week"], "").strip()
        if not w:
            w = timestamp_to_week(r.get(DFY["created_at"], ""))
        r["_week"] = w
        filtered.append(r)
    print(f"  Dragonfly: {len(filtered)} rows after filter")

    all_dfy_weeks = sorted({r["_week"] for r in filtered if r["_week"]})
    if not all_dfy_weeks:
        print("  Dragonfly: no week data found")
        return {}, {}

    # Use latest_week from Incidents if available, else Dragonfly's own latest
    week = latest_week if latest_week else all_dfy_weeks[-1]

    zero_dfy = lambda: {"total": 0, "closed": 0, "open": 0, "feedback": 0,
                         "first_timers": 0, "positive_sent": 0, "qri_sum": 0.0, "qri_count": 0,
                         "days_comp_sum": 0.0, "days_comp_count": 0,
                         "days_resp_sum": 0.0, "days_resp_count": 0,
                         "submitters": set(), "candidates": []}

    site_week_dfy = defaultdict(lambda: defaultdict(zero_dfy))

    for r in filtered:
        site = r.get(DFY["site"], "").strip()
        w = r["_week"]
        d = site_week_dfy[site][w]
        d["total"] += 1
        status = r.get(DFY["status"], "").strip().lower()
        if "closed" in status or "complete" in status:
            d["closed"] += 1
        else:
            d["open"] += 1
        has_fb = r.get(DFY["has_feedback"], "").strip().lower()
        if has_fb in ("yes", "true", "1"):
            d["feedback"] += 1
        ft = str(r.get(DFY["first_time"], "")).strip().lower()
        if ft in ("yes", "true", "1"):
            d["first_timers"] += 1
        sent = r.get(DFY["sentiment"], "") or r.get(DFY["sentiment_desc"], "")
        if is_positive_sentiment(sent):
            d["positive_sent"] += 1
        qri_val = pf(r.get(DFY["qri"]))
        if qri_val > 0:
            d["qri_sum"] += qri_val
            d["qri_count"] += 1
        dc = pf(r.get(DFY["days_completion"]))
        if dc > 0:
            d["days_comp_sum"] += dc
            d["days_comp_count"] += 1
        dr = pf(r.get(DFY["days_response"]))
        if dr > 0:
            d["days_resp_sum"] += dr
            d["days_resp_count"] += 1
        d["submitters"].add(r.get(DFY["login"], "").strip())
        score, ft_s = dfy_score(r)
        d["candidates"].append((score, ft_s, r))

    # YTD per site
    zero_dfy2 = lambda: {"total": 0, "closed": 0, "open": 0, "feedback": 0,
                          "first_timers": 0, "positive_sent": 0, "qri_sum": 0.0, "qri_count": 0,
                          "days_comp_sum": 0.0, "days_comp_count": 0,
                          "days_resp_sum": 0.0, "days_resp_count": 0,
                          "submitters": set()}
    site_ytd_dfy = defaultdict(zero_dfy2)
    for site, weeks in site_week_dfy.items():
        for d in weeks.values():
            y = site_ytd_dfy[site]
            for k in ["total","closed","open","feedback","first_timers","positive_sent","qri_count","days_comp_count","days_resp_count"]:
                y[k] += d[k]
            for k in ["qri_sum","days_comp_sum","days_resp_sum"]:
                y[k] += d[k]
            y["submitters"] |= d["submitters"]

    return site_week_dfy, site_ytd_dfy


# ── Build best DFY description per site ───────────────────────────────────────
def build_dfy_descriptions(site_week_dfy, all_sites):
    descriptions = {}
    all_candidates = []
    for site, weeks in site_week_dfy.items():
        for d in weeks.values():
            all_candidates.extend(d["candidates"])
    all_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)

    seen = set()
    for score, ft_s, row in all_candidates:
        site = row.get(DFY["site"], "").strip()
        if site.upper() in seen:
            continue
        seen.add(site.upper())
        desc = truncate(row.get(DFY["observation"], ""))
        desc_en = translate_text(desc)
        login = row.get(DFY["login"], "").strip()
        hist = sum(1 for _, _, r in all_candidates if r.get(DFY["login"], "").strip() == login)
        date = (row.get(DFY["created_at"], "") or "").strip().split(" ")[0]
        shoutout = ("\n\n💪 Above and beyond! Recognize them: https://atoz.amazon.work/shout-outs\n"
                    if site.upper() in BLUE_BADGE_SITES else "")
        full = f"📦 {site}       👤 @{login}       ✍️ {hist} obs.\n\n{desc_en}{shoutout}"
        descriptions[site.upper()] = {"desc": full, "date": date}
        print(f"  DFY description: {site}")
    return descriptions


# ── Load & aggregate Inspections ──────────────────────────────────────────────
def load_inspections():
    rows = read_csv(INSPECTIONS_CSV)
    zero_insp = lambda: {"due_insp": 0, "otc_insp": 0, "due_tasks": 0, "otc_tasks": 0,
                          "on_time": 0, "overdue": 0, "tasks_on_time": 0, "tasks_overdue": 0}
    site_week_insp = defaultdict(lambda: defaultdict(zero_insp))

    all_weeks = sorted({r.get(INSP["week"], "").strip() for r in rows if r.get(INSP["week"], "").strip()})
    latest = all_weeks[-1] if all_weeks else ""

    for r in rows:
        site = r.get(INSP["site"], "").strip()
        week = r.get(INSP["week"], "").strip()
        if not site or not week:
            continue
        d = site_week_insp[site][week]
        d["due_insp"]      += pi(r.get(INSP["due_insp"]))
        d["otc_insp"]      += pi(r.get(INSP["otc_insp"]))
        d["due_tasks"]     += pi(r.get(INSP["due_tasks"]))
        d["otc_tasks"]     += pi(r.get(INSP["otc_tasks"]))
        d["on_time"]       += pi(r.get(INSP["on_time"]))
        d["overdue"]       += pi(r.get(INSP["overdue"]))
        d["tasks_on_time"] += pi(r.get(INSP["tasks_on_time"]))
        d["tasks_overdue"] += pi(r.get(INSP["tasks_overdue"]))

    site_ytd_insp = defaultdict(zero_insp)
    for site, weeks in site_week_insp.items():
        for d in weeks.values():
            for k in site_ytd_insp[site]:
                site_ytd_insp[site][k] += d[k]

    print(f"  Inspections: {sum(len(w) for w in site_week_insp.values())} site-weeks")
    return site_week_insp, site_ytd_insp, latest


# ── Load manual input ─────────────────────────────────────────────────────────
def load_manual(latest_week):
    rows = read_csv(MANUAL_CSV)
    manual = {}
    for r in rows:
        if r.get("Week", "").strip() == latest_week:
            site = r.get("Site", "").strip().upper()
            manual[site] = {
                "story": r.get("Success_Story", ""),
                "tip": r.get("Tip", ""),
                "by": r.get("Submitted_By", ""),
            }
    print(f"  Manual inputs for {latest_week}: {len(manual)}")
    return manual


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Flash Report Unificado")
    print("=" * 55)

    print("\n[1/5] Incidents...")
    site_week_inc, site_ytd_inc, site_meta, latest_week, prev_week = load_incidents()

    print("\n[2/5] Dragonfly...")
    site_week_dfy, site_ytd_dfy = load_dragonfly(latest_week)

    print("\n[3/5] Dragonfly descriptions...")
    all_sites_dfy = set(site_week_dfy.keys())
    dfy_desc = build_dfy_descriptions(site_week_dfy, all_sites_dfy)

    print("\n[4/5] Inspections...")
    site_week_insp, site_ytd_insp, _ = load_inspections()

    print("\n[5/5] Manual inputs...")
    manual = load_manual(latest_week)

    # Union of all sites
    all_sites = sorted(
        set(site_week_inc.keys()) | set(site_week_dfy.keys()) | set(site_week_insp.keys())
    )
    print(f"\n  Building output for {len(all_sites)} sites...")

    zero_inc = {k: 0.0 for k in ["hours","all","si","ri","dart","lti","fai","msd_ri","msd_lti","near_miss","pit_all","pit_si","pit_ri","yard","pit_ped"]}
    zero_dfy_w = {"total": 0, "closed": 0, "open": 0, "feedback": 0, "first_timers": 0,
                  "positive_sent": 0, "qri_sum": 0.0, "qri_count": 0,
                  "days_comp_sum": 0.0, "days_comp_count": 0,
                  "days_resp_sum": 0.0, "days_resp_count": 0,
                  "submitters": set(), "candidates": []}
    zero_insp_w = {"due_insp": 0, "otc_insp": 0, "due_tasks": 0, "otc_tasks": 0,
                   "on_time": 0, "overdue": 0, "tasks_on_time": 0, "tasks_overdue": 0}

    results = []
    for site in all_sites:
        meta = site_meta.get(site, {"bu": "", "sub_bu": "", "year": "", "quarter": "", "month": ""})
        lat, lon = COORDINATES.get(site.upper(), ("", ""))

        ci = site_week_inc[site].get(latest_week, zero_inc)
        pi_ = site_week_inc[site].get(prev_week, zero_inc)
        yi = site_ytd_inc[site]

        cd = site_week_dfy[site].get(latest_week, zero_dfy_w) if site in site_week_dfy else zero_dfy_w
        yd = site_ytd_dfy[site] if site in site_ytd_dfy else {"total": 0, "closed": 0, "open": 0,
             "feedback": 0, "first_timers": 0, "positive_sent": 0, "qri_sum": 0.0, "qri_count": 0,
             "days_comp_sum": 0.0, "days_comp_count": 0, "days_resp_sum": 0.0,
             "days_resp_count": 0, "submitters": set()}

        cs = site_week_insp[site].get(latest_week, zero_insp_w) if site in site_week_insp else zero_insp_w
        ys = site_ytd_insp[site] if site in site_ytd_insp else zero_insp_w.copy()

        desc_data = dfy_desc.get(site.upper(), {"desc": "", "date": ""})
        man = manual.get(site.upper(), {"story": "", "tip": "", "by": ""})

        row = {
            "Site": site,
            "BU": meta["bu"],
            "Sub_BU": meta["sub_bu"],
            "Latitude": lat,
            "Longitude": lon,
            "Total_Hours_Week": f"{ci['hours']:.0f}",
            "Total_Hours_YTD": f"{yi['hours']:.0f}",
            "Year": meta["year"],
            "Quarter": meta["quarter"],
            "Month": meta["month"],
            "Week": latest_week,
            # INC counts
            "INC_All_Week": f"{ci['all']:.0f}",        "INC_All_YTD": f"{yi['all']:.0f}",
            "INC_SI_Week": f"{ci['si']:.0f}",          "INC_SI_YTD": f"{yi['si']:.0f}",
            "INC_RI_Week": f"{ci['ri']:.0f}",          "INC_RI_YTD": f"{yi['ri']:.0f}",
            "INC_DART_Week": f"{ci['dart']:.0f}",      "INC_DART_YTD": f"{yi['dart']:.0f}",
            "INC_LTI_Week": f"{ci['lti']:.0f}",        "INC_LTI_YTD": f"{yi['lti']:.0f}",
            "INC_FAI_Week": f"{ci['fai']:.0f}",        "INC_FAI_YTD": f"{yi['fai']:.0f}",
            "INC_MSD_RI_Week": f"{ci['msd_ri']:.0f}",  "INC_MSD_RI_YTD": f"{yi['msd_ri']:.0f}",
            "INC_MSD_LTI_Week": f"{ci['msd_lti']:.0f}",
            "INC_Near_Miss_Week": f"{ci['near_miss']:.0f}", "INC_Near_Miss_YTD": f"{yi['near_miss']:.0f}",
            "INC_PIT_All_Week": f"{ci['pit_all']:.0f}",
            "INC_PIT_SI_Week": f"{ci['pit_si']:.0f}",
            "INC_PIT_RI_Week": f"{ci['pit_ri']:.0f}",
            "INC_Yard_Week": f"{ci['yard']:.0f}",
            "INC_PIT_Ped_Week": f"{ci['pit_ped']:.0f}",
            # INC rates
            "INC_RIR_Week": fmt(rate(ci['ri'], ci['hours'])),
            "INC_RIR_YTD": fmt(rate(yi['ri'], yi['hours'])),
            "INC_SIR_Week": fmt(rate(ci['si'], ci['hours'])),
            "INC_SIR_YTD": fmt(rate(yi['si'], yi['hours'])),
            "INC_DART_Rate_Week": fmt(rate(ci['dart'], ci['hours'])),
            "INC_DART_Rate_YTD": fmt(rate(yi['dart'], yi['hours'])),
            "INC_LTIR_Week": fmt(rate(ci['lti'], ci['hours'])),
            "INC_LTIR_YTD": fmt(rate(yi['lti'], yi['hours'])),
            "INC_MSD_RIR_Week": fmt(rate(ci['msd_ri'], ci['hours'])),
            "INC_MSD_RIR_YTD": fmt(rate(yi['msd_ri'], yi['hours'])),
            "INC_FAIR_Week": fmt(rate(ci['fai'], ci['hours'])),
            "INC_FAIR_YTD": fmt(rate(yi['fai'], yi['hours'])),
            # INSP legacy (mirrors Week)
            "INSP_Due_Inspections": cs["due_insp"],
            "INSP_Inspection_OTC": cs["otc_insp"],
            "INSP_Due_Tasks": cs["due_tasks"],
            "INSP_Task_OTC": cs["otc_tasks"],
            "INSP_On_Time": cs["on_time"],
            "INSP_Overdue": cs["overdue"],
            "INSP_Tasks_On_Time": cs["tasks_on_time"],
            "INSP_Tasks_Overdue": cs["tasks_overdue"],
            # DFY metrics
            "DFY_Total_Obs_Week": cd["total"],       "DFY_Total_Obs_YTD": yd["total"],
            "DFY_Closed_Week": cd["closed"],         "DFY_Closed_YTD": yd["closed"],
            "DFY_Open_Week": cd["open"],             "DFY_Open_YTD": yd["open"],
            "DFY_Closure_Rate_Week": fmt(pct(cd["closed"], cd["total"])),
            "DFY_Closure_Rate_YTD": fmt(pct(yd["closed"], yd["total"])),
            "DFY_Feedback_Rate_Week": fmt(pct(cd["feedback"], cd["total"])),
            "DFY_Feedback_Rate_YTD": fmt(pct(yd["feedback"], yd["total"])),
            "DFY_First_Timers_Week": cd["first_timers"],
            "DFY_First_Timers_YTD": yd["first_timers"],
            "DFY_Sentiment_Positive_Pct_Week": fmt(pct(cd["positive_sent"], cd["total"])),
            "DFY_Sentiment_Positive_Pct_YTD": fmt(pct(yd["positive_sent"], yd["total"])),
            "DFY_QRI_Avg_Week": fmt(avg(cd["qri_sum"], cd["qri_count"])),
            "DFY_QRI_Avg_YTD": fmt(avg(yd["qri_sum"], yd["qri_count"])),
            "DFY_Days_Completion_Avg_Week": fmt(avg(cd["days_comp_sum"], cd["days_comp_count"])),
            "DFY_Days_Completion_Avg_YTD": fmt(avg(yd["days_comp_sum"], yd["days_comp_count"])),
            "DFY_Days_Response_Avg_Week": fmt(avg(cd["days_resp_sum"], cd["days_resp_count"])),
            "DFY_Days_Response_Avg_YTD": fmt(avg(yd["days_resp_sum"], yd["days_resp_count"])),
            "DFY_Rate_Week": fmt(rate(cd["total"], ci["hours"])),
            "DFY_Rate_YTD": fmt(rate(yd["total"], yi["hours"])),
            "DFY_Submitter_Rate_Week": fmt(rate(len(cd["submitters"]), ci["hours"])),
            "DFY_Submitter_Rate_YTD": fmt(rate(len(yd["submitters"]), yi["hours"])),
            "DFY_Description": desc_data["desc"],
            "DFY_Date": desc_data["date"],
            # INSP Week + YTD
            "INSP_Due_Insp_Week": cs["due_insp"],       "INSP_Due_Insp_YTD": ys["due_insp"],
            "INSP_OTC_Week": cs["otc_insp"],             "INSP_OTC_YTD": ys["otc_insp"],
            "INSP_Due_Tasks_Week": cs["due_tasks"],      "INSP_Due_Tasks_YTD": ys["due_tasks"],
            "INSP_Task_OTC_Week": cs["otc_tasks"],       "INSP_Task_OTC_YTD": ys["otc_tasks"],
            "INSP_On_Time_Week": cs["on_time"],          "INSP_On_Time_YTD": ys["on_time"],
            "INSP_Overdue_Week": cs["overdue"],          "INSP_Overdue_YTD": ys["overdue"],
            "INSP_Tasks_On_Time_Week": cs["tasks_on_time"], "INSP_Tasks_On_Time_YTD": ys["tasks_on_time"],
            "INSP_Tasks_Overdue_Week": cs["tasks_overdue"], "INSP_Tasks_Overdue_YTD": ys["tasks_overdue"],
            # Manual
            "Manual_Success_Story": man["story"],
            "Manual_Tip": man["tip"],
            "Manual_Submitted_By": man["by"],
        }
        results.append(row)
        print(f"  {site} - done")

    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Done! {len(results)} sites → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
