@echo off
echo Setting UTF-8 encoding for Windows...
chcp 65001 > nul

set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1
set PYTHONUNBUFFERED=1

echo Starting CS466 Learning System with UTF-8 support...
python main.py

pause 