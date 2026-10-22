@echo off
setlocal
cd /d %~dp0

rem Recreate the virtual environment if it is missing or was copied from another machine
if exist .venv\Scripts\python.exe (
	.venv\Scripts\python.exe -c "import sys" >nul 2>&1 || rmdir /s /q .venv
)
if not exist .venv (
	python -m venv .venv
)
call .venv\Scripts\activate

python -m pip install --upgrade pip >nul
pip install -r requirements.txt

python seed.py
python run.py
