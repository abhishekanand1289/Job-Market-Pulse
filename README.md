# Job Market Pulse — Automated Job Data Pipeline

An end-to-end automated data pipeline that collects live job postings daily from public job boards and government APIs, stores them in a structured MySQL database, and maintains a growing dataset for job market trend analysis.

**Pipeline has been running since July 11, 2025 — collecting 2,000+ postings daily across 20 job categories.**

---

## The Problem

Job seekers apply blindly without knowing where real hiring activity is, what roles are actually in demand, or how salaries compare across sources. There is no single place that shows live job market intelligence — updated daily, not monthly.

This pipeline is the data foundation for solving that problem.

---

## What This Project Demonstrates

- Building and automating a production-style data ingestion pipeline
- Integrating multiple data sources (REST API + web scraping) into a unified schema
- Designing a MySQL database with deduplication logic using upsert patterns
- Scheduling fully automated daily runs using Windows Task Scheduler
- Version controlling code and data with Git and GitHub

---

## Pipeline Architecture

```
USAJobs REST API          LinkedIn + Indeed
(Federal postings)        (Private sector)
        |                       |
        └──────────┬────────────┘
                   ↓
           Python Collector
           (Pull_Job_Postings.py)
                   ↓
         Data Cleaning & Dedup
         (Normalize schema,
          remove duplicates)
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
   MySQL Database         CSV Snapshot
   (job_postings)         (daily backup)
        ↓
   GitHub Backup
   (automated commit)
```

---

## Data Collected

| Source | Type | Daily Volume |
|---|---|---|
| USAJobs API | Federal government jobs | ~500 postings |
| LinkedIn | Private sector | ~950 postings |
| Indeed | Private sector | ~700 postings |
| **Total** | | **~2,000+ unique postings/day** |

**Keywords tracked (20 roles):**
Data Analyst, Data Engineer, Data Scientist, Business Analyst, Business Intelligence Analyst, Analytics Engineer, Quantitative Analyst, Software Engineer, Cloud Engineer, DevOps Engineer, Machine Learning Engineer, AI Engineer, IT Specialist, Systems Analyst, Database Administrator, Network Engineer, Cybersecurity Analyst, Program Analyst, Project Manager, Operations Analyst

**Fields captured per posting:**
Source, Job ID, Title, Company, Department, Location, Salary Min/Max, Salary Interval, Posted Date, Close Date, Job URL, Job Summary, Work Schedule, Position Type, Security Clearance, Remote Status, Collected At

---

## Database Schema

```sql
CREATE TABLE job_postings (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    source              VARCHAR(50),
    search_keyword      VARCHAR(100),
    job_id              VARCHAR(255),
    title               VARCHAR(300),
    company             VARCHAR(300),
    department          VARCHAR(300),
    location            TEXT,
    salary_min          DECIMAL(12,2),
    salary_max          DECIMAL(12,2),
    salary_interval     VARCHAR(50),
    posted_date         DATE,
    close_date          DATE,
    job_url             TEXT,
    job_summary         TEXT,
    work_schedule       TEXT,
    position_type       TEXT,
    security_clearance  VARCHAR(100),
    remote              VARCHAR(100),
    collected_at        DATETIME,
    UNIQUE KEY uq_source_job (source, job_id(100))
);
```

The `UNIQUE KEY` on `(source, job_id)` ensures the same posting is never inserted twice — the pipeline uses upsert logic so duplicate runs update existing records rather than creating duplicates.

---

## How It Runs Automatically

**Windows Task Scheduler** triggers `run_collector.bat` every day at 7:30 PM:

```
run_collector.bat
    → Pull_Job_Postings.py   (collect from all 3 sources)
    → load_to_Database.py    (clean, deduplicate, load to MySQL)
    → git add + commit + push (backup to GitHub)
```

No manual intervention required after setup.

---

## Repository Structure

```
Job-Market-Pulse/
├── Pull_Job_Postings.py     # Collects from USAJobs API, LinkedIn, Indeed
├── load_to_Database.py      # Cleans data and loads to MySQL with upsert logic
├── daily_run.py             # Orchestrator — runs both scripts in sequence
├── run_collector.bat        # Windows Task Scheduler entry point
├── requirements.txt         # Python dependencies
├── data/                    # CSV snapshots — one file per collection run
│   └── jobs_combined_*.csv
└── README.md
```

---

## Setup & Replication

**Requirements:**
- Python 3.11+
- MySQL 8.0+
- Windows (for Task Scheduler automation)

**Install dependencies:**
```bash
pip install requests pandas python-jobspy mysql-connector-python
```

**Configure credentials:**
```python
# In Pull_Job_Postings.py
API_KEY = "your_usajobs_api_key"   # Free at developer.usajobs.gov
EMAIL   = "your_registered_email"

# In load_to_Database.py
password = "your_mysql_password"
```

**Create the database:**
```sql
CREATE DATABASE job_postings;
USE job_postings;
-- Run the schema above
```

**Run manually:**
```bash
python daily_run.py
```

**Schedule automatically:**
Point Windows Task Scheduler to `run_collector.bat` at your preferred daily time.

---

## Current Dataset

| Metric | Value |
|---|---|
| Collection started | July 11, 2025 |
| Total postings collected | 43,347+ and growing |
| Collection frequency | Daily |
| Sources | USAJobs, LinkedIn, Indeed |
| Job categories | 20 |

---

## Key Technical Decisions

**Why upsert instead of insert?**
The same job posting appears across multiple collection runs. Using `INSERT ... ON DUPLICATE KEY UPDATE` ensures the database reflects the latest state of each posting without duplication — the same pattern used in production ETL systems.

**Why CSV backups alongside MySQL?**
If the database needs to be rebuilt, every CSV snapshot is a complete recovery point. This mirrors production data engineering practice — always maintain a raw data layer separate from the processed layer.

**Why jobspy for LinkedIn and Indeed?**
No official API exists for private job boards. jobspy is a well-maintained open-source scraper that handles both sites reliably, allowing the pipeline to collect private sector data alongside the official USAJobs API without managing separate scraping infrastructure.

---

## Next Phase

With months of daily data accumulating, the next phase is analysis and visualization:
- Salary trends by role and location over time
- Which job categories are growing vs declining week over week
- Geographic concentration of hiring activity
- Skills frequency analysis from job descriptions

---

## Tools & Skills

| Category | Tools |
|---|---|
| Data Collection | Python, requests, python-jobspy |
| Database | MySQL, SQL |
| Automation | Windows Task Scheduler, Batch scripting |
| Version Control | Git, GitHub |
| Data Processing | pandas, numpy |
| API Integration | USAJobs REST API |

---

Built by **Abhishek Anand Battini** | [LinkedIn](https://linkedin.com/in/abhishekanandb) | [GitHub](https://github.com/abhishekanand1289)
