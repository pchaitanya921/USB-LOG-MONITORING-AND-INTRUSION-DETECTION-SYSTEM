@echo off
echo Installing YARA for Enhanced Malware Detection
echo =============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

echo Running with administrator privileges...
echo.

echo Step 1: Installing yara-python...
pip install yara-python

echo.
echo Step 2: Verifying installation...
python -c "import yara; print('YARA module installed successfully!')" || echo YARA module installation failed.

echo.
echo Installation completed!
echo.
echo If the installation was successful, the USB monitoring system will now use YARA rules
echo for enhanced malware detection capabilities.
echo.
echo If the installation failed, the system will still work but without YARA scanning.
echo.
pause
