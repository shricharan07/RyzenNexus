@echo off
:: ... (Keep the Admin/UAC section at the top the same) ...

:gotAdmin
    pushd "%CD%"

:: Step 1: Start the AI Backend from the engine subfolder
start /min python engine/server.py

:: Step 2: Wait 3 seconds for the AI Brain to load
timeout /t 3 /nobreak >nul

:: Step 3: Launch the Dashboard from the gui subfolder
start gui\index.html

echo [SUCCESS] Ryzen Nexus is now managing your hardware.
pause