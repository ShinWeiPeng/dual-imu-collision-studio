@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
if errorlevel 1 goto directory_failed

if exist ".venv\Scripts\python.exe" goto existing_environment
echo [Info] Checking bootstrap Python...
python --version
if errorlevel 1 goto python_failed
python -u "tools\launch_studio.py"
goto finished

:existing_environment
".venv\Scripts\python.exe" -u "tools\launch_studio.py"

:finished
set "launcher_exit=%errorlevel%"
if "%launcher_exit%"=="0" exit /b 0
echo [ERROR] Startup failed or readiness was not confirmed. Exit code: %launcher_exit%
echo [Info] Review the messages and startup log above.
echo Press any key to close this window.
pause >nul
exit /b %launcher_exit%

:python_failed
echo [ERROR] Python is unavailable. Install Python 3.11 or newer and enable it on PATH.
echo Press any key to close this window.
pause >nul
exit /b 1

:directory_failed
echo [ERROR] Cannot enter the application directory.
echo Press any key to close this window.
pause >nul
exit /b 1
