@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call "%~dp0update.bat"
  if errorlevel 1 exit /b 1
)
call "%~dp0.venv\Scripts\activate.bat"
"%~dp0.venv\Scripts\python.exe" "%~dp0example\__main__.py"
exit /b %ERRORLEVEL%
