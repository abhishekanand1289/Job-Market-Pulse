import subprocess
import sys

python = sys.executable

print("Step 1: Pulling jobs...")
subprocess.run([python, "Pull_Job_Postings.py"])

print("Step 2: Loading to database...")
subprocess.run([python, "load_to_Database.py"])

print("Done!")