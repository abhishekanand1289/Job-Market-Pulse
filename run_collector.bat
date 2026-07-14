@echo off
save_path = "C:/Users/ahishekanand/Desktop/Job Market Pulse/Daily data puller/data"
C:\Windows\py.exe -3.11 daily_run.py

git add data/
git commit -m "daily backup: %date%"
git push