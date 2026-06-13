@echo off
setlocal EnableExtensions
rem Pack onefile via PyInstaller; no staticx on Windows.
rem Usage from repo root: tools\pack.bat [src]
rem Outputs: dist\consolver.exe and dist\consolver-<version>-windows.zip
rem Spec: consolver-cli.spec at repo root.
cd /d "%~dp0\.."

set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=src"

if not exist ".venv\Scripts\python.exe" (
    echo Creating .venv ...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo ERROR: failed to create .venv
        exit /b 1
    )
)

set "PY=%CD%\.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo ERROR: missing %PY%
    exit /b 1
)

echo ==^> venv: %PY%
"%PY%" -V

"%PY%" -m pip install -q -U pip setuptools wheel
if errorlevel 1 exit /b 1
"%PY%" -m pip install -q --upgrade --force-reinstall --only-binary=z3-solver -e ".[dev]"
if errorlevel 1 exit /b 1
"%PY%" -m pip install -q --upgrade --force-reinstall "pyinstaller>=6.0"
if errorlevel 1 exit /b 1

if /I not "%TARGET%"=="src" (
    echo Usage: tools\pack.bat [src] >&2
    exit /b 1
)

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

set "SPEC=%CD%\consolver-cli.spec"
if not exist "%SPEC%" (
    echo ERROR: missing %SPEC% >&2
    exit /b 1
)

echo ==^> PyInstaller: %SPEC%
"%PY%" -m PyInstaller --clean --noconfirm "%SPEC%"
if errorlevel 1 exit /b 1

if exist "%CD%\dist\consolver.exe" (
    echo Done: %CD%\dist\consolver.exe
) else (
    echo ERROR: dist\consolver.exe not found >&2
    exit /b 1
)

echo ==^> bundle release archive
"%PY%" tools\bundle_release.py
if errorlevel 1 exit /b 1

echo Output: %CD%\dist
exit /b 0
