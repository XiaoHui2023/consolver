@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 exit /b 1
)
call "%~dp0.venv\Scripts\activate.bat"
python -m pip install -U pip
python -m pip install "z3-solver>=4.12" "pytest>=8.0" "PyYAML>=6.0" "Jinja2>=3.1"
exit /b %ERRORLEVEL%
