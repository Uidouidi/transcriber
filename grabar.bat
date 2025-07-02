@echo off
cd /d %~dp0
call ..\Scripts\activate
python main.py
pause
