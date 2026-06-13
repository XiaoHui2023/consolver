@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."

if exist ".venv" rmdir /s /q ".venv"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

python -V
if errorlevel 1 exit /b 1
python -m pip install -U pip setuptools wheel
if errorlevel 1 exit /b 1
python -m pip install --only-binary=z3-solver ".[dev]"
if errorlevel 1 exit /b 1
python -m pip install --upgrade "pyinstaller>=6.0" tzdata
if errorlevel 1 exit /b 1

python -m PyInstaller --clean --noconfirm "consolver-cli.spec"
if errorlevel 1 exit /b 1
if not exist "dist\consolver.exe" exit /b 1

python tools\bundle_release.py
if errorlevel 1 exit /b 1

exit /b 0
