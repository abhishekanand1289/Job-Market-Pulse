import pandas as pd
import numpy as np
import mysql.connector
import glob
import os


conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='@1289Royal',
    database='job_postings'
)
cursor = conn.cursor()


csv_folder = "C:/Users/ahishekanand/Desktop/Job Market Pulse/data/"
csv_files  = glob.glob(csv_folder + "jobs_combined_*.csv")
latest_csv = max(csv_files, key=os.path.getctime)


df = pd.read_csv(latest_csv)



df = df.replace({np.nan: None, 'nan': None, 'None': None, '': None})

for col in ['posted_date', 'close_date']:
    df[col] = df[col].apply(lambda x: x if x and x != 'nan' else None)


df['location']      = df['location'].apply(lambda x: x[:500] if x else None)
df['work_schedule'] = df['work_schedule'].apply(lambda x: x[:100] if x else None)
df['position_type'] = df['position_type'].apply(lambda x: x[:100] if x else None)
df['company']       = df['company'].apply(lambda x: x[:300] if x else None)
df['title']         = df['title'].apply(lambda x: x[:300] if x else None)


insert_sql = """
INSERT INTO postings (
    source, keyword, job_id, title, company, department,
    location, salary_min, salary_max, salary_interval,
    posted_date, close_date, job_url, job_summary,
    work_schedule, position_type, security_clearance, remote, collected_at
) VALUES (
    %(source)s, %(search_keyword)s, %(job_id)s, %(title)s,
    %(company)s, %(department)s, %(location)s,
    %(salary_min)s, %(salary_max)s, %(salary_interval)s,
    %(posted_date)s, %(close_date)s, %(job_url)s, %(job_summary)s,
    %(work_schedule)s, %(position_type)s, %(security_clearance)s,
    %(remote)s, %(collected_at)s
)
ON DUPLICATE KEY UPDATE
    title        = VALUES(title),
    salary_min   = VALUES(salary_min),
    salary_max   = VALUES(salary_max),
    job_summary  = VALUES(job_summary),
    collected_at = VALUES(collected_at);
"""

new_rows = 0
skipped  = 0

for record in df.to_dict("records"):
    try:
        cursor.execute(insert_sql, record)
        if cursor.rowcount == 1:
            new_rows += 1
        else:
            skipped += 1
    except Exception as e:
        print(f"Row skipped: {e}")

conn.commit()
cursor.close()
conn.close()

