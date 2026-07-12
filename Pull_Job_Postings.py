import requests
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
import os

API_KEY = "WYvjQd/FlCzygwHh1hQ9bjEWflR+6GhiiVEFIpvrT+o="
EMAIL   = "a.battini@myemail.indwes.edu"

KEYWORDS = [
    "data analyst", "data engineer", "data scientist", "business analyst",
    "business intelligence analyst", "analytics engineer", "quantitative analyst",
    "software engineer", "cloud engineer", "DevOps engineer",
    "machine learning engineer", "AI engineer",
    "IT specialist", "systems analyst", "database administrator",
    "network engineer", "cybersecurity analyst",
    "program analyst", "project manager", "operations analyst"
]

def fetch_usajobs(keyword):
    headers = {
        "Authorization-Key": API_KEY,
        "User-Agent": EMAIL,
        "Host": "data.usajobs.gov"
    }
    r = requests.get(
        "https://data.usajobs.gov/api/search",
        headers=headers,
        params={"Keyword": keyword, "ResultsPerPage": 50}
    )
    items = r.json()["SearchResult"]["SearchResultItems"]
    rows = []
    for item in items:
        d = item["MatchedObjectDescriptor"]
        rows.append({
            "source":             "USAJobs",
            "search_keyword":     keyword,
            "job_id":             d.get("PositionID", ""),
            "title":              d.get("PositionTitle", ""),
            "company":            d.get("OrganizationName", ""),
            "department":         d.get("DepartmentName", ""),
            "location":           ", ".join([l.get("LocationName", "") for l in d.get("PositionLocation", [])]),
            "salary_min":         d.get("PositionRemuneration", [{}])[0].get("MinimumRange", None),
            "salary_max":         d.get("PositionRemuneration", [{}])[0].get("MaximumRange", None),
            "salary_interval":    d.get("PositionRemuneration", [{}])[0].get("RateIntervalCode", None),
            "posted_date":        d.get("PublicationStartDate", "")[:10],
            "close_date":         d.get("ApplicationCloseDate", "")[:10],
            "job_url":            d.get("PositionURI", ""),
            "job_summary":        d.get("UserArea", {}).get("Details", {}).get("JobSummary", "")[:500],
            "work_schedule":      d.get("PositionSchedule", [{}])[0].get("Name", ""),
            "position_type":      d.get("PositionOfferingType", [{}])[0].get("Name", ""),
            "security_clearance": d.get("UserArea", {}).get("Details", {}).get("SecurityClearance", ""),
            "remote":             None,
            "collected_at":       datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        })
    return rows

def fetch_web_jobs(keyword):
    try:
        df = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=keyword,
            location="United States",
            results_wanted=50,
            hours_old=168,
            country_indeed="USA"
        )
        rows = []
        for _, r in df.iterrows():
            rows.append({
                "source":             str(r.get("site", "")).title(),
                "search_keyword":     keyword,
                "job_id":             str(r.get("id", "")),
                "title":              r.get("title", ""),
                "company":            r.get("company", ""),
                "department":         None,
                "location":           r.get("location", ""),
                "salary_min":         r.get("min_amount", None),
                "salary_max":         r.get("max_amount", None),
                "salary_interval":    r.get("interval", None),
                "posted_date":        str(r.get("date_posted", ""))[:10],
                "close_date":         None,
                "job_url":            r.get("job_url", ""),
                "job_summary":        str(r.get("description", ""))[:500],
                "work_schedule":      str(r.get("job_type", "")),
                "position_type":      None,
                "security_clearance": None,
                "remote":             r.get("work_from_home_type", None),
                "collected_at":       datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            })
        return rows
    except Exception as e:
        print(f"  Error: {e}")
        return []

# ── Main ─────────────────────────────────────────────────────
print("Starting collection...")
all_rows = []
seen_ids = set()

for keyword in KEYWORDS:
    print(f"Collecting: {keyword}")

    usa_rows = fetch_usajobs(keyword)
    for row in usa_rows:
        uid = f"usajobs_{row['job_id']}"
        if uid not in seen_ids:
            seen_ids.add(uid)
            all_rows.append(row)
    print(f"  USAJobs: {len(usa_rows)}")

    web_rows = fetch_web_jobs(keyword)
    for row in web_rows:
        uid = f"{row['source']}_{row['job_id']}"
        if uid not in seen_ids:
            seen_ids.add(uid)
            all_rows.append(row)
    print(f"  Web: {len(web_rows)}")

df_combined = pd.DataFrame(all_rows)
print(f"\nTotal: {len(df_combined)} unique jobs")
print(df_combined['source'].value_counts())

save_path = "C:/Users/ahishekanand/Desktop/Job Market Pulse/data"
os.makedirs(save_path, exist_ok=True)
date_str  = datetime.utcnow().strftime("%Y%m%d_%H%M")
filename  = f"{save_path}/jobs_combined_{date_str}.csv"
df_combined.to_csv(filename, index=False)
print(f"Saved → {filename}")




