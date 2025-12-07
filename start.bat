@echo off
setlocal
cd /d %~dp0

if not exist .venv (
	python -m venv .venv
)
call .venv\Scripts\activate

python -m pip install --upgrade pip >nul
pip install -r requirements.txt

python seed.py
python run.py



