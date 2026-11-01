@echo off
rem Double-click to open the preview: installs the dependencies on the first run, then starts the local server
rem and opens the page in your browser. Close this window (or press Ctrl+C) to stop it.
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 goto nonode
if exist "node_modules\playwright-core" goto run
echo Installing dependencies (first run only)...
call npm install
if errorlevel 1 goto failed
:run
call npm run preview
goto end
:nonode
echo Node.js 20 or newer is required: https://nodejs.org/
goto end
:failed
echo npm install failed. See the messages above.
:end
pause
