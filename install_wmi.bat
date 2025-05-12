@echo off
echo WMI Module Installation Helper
echo ============================
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

python install_wmi.py

echo.
if %errorLevel% equ 0 (
    echo WMI installation completed successfully!
) else (
    echo WMI installation encountered issues. Please check the output above.
)
echo.
pause
