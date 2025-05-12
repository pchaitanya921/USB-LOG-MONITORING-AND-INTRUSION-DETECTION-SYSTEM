@echo off
echo USB Monitoring System - Enhanced Edition
echo ======================================
echo.

:MENU
cls
echo USB Monitoring System - Enhanced Edition
echo ======================================
echo.
echo Choose an option:
echo 1. Start USB Monitoring System
echo 2. Install YARA for Enhanced Malware Detection
echo 3. Set Up Automatic Startup
echo 4. Test Notifications
echo 5. View Documentation
echo 6. Exit
echo.

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto START
if "%choice%"=="2" goto INSTALL_YARA
if "%choice%"=="3" goto SETUP_AUTOSTART
if "%choice%"=="4" goto TEST_NOTIFICATIONS
if "%choice%"=="5" goto VIEW_DOCS
if "%choice%"=="6" goto END

echo Invalid choice. Please try again.
echo.
pause
goto MENU

:START
cls
echo Starting USB Monitoring System...
echo.
echo The web interface will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.
start http://localhost:5000
python clean_app.py
goto MENU

:INSTALL_YARA
cls
echo Installing YARA for Enhanced Malware Detection...
echo.
call install_yara.bat
echo.
pause
goto MENU

:SETUP_AUTOSTART
cls
echo Setting Up Automatic Startup...
echo.
call setup_autostart.bat
echo.
pause
goto MENU

:TEST_NOTIFICATIONS
cls
echo Testing Notifications...
echo.
echo This will send test notifications to your configured email and SMS.
echo Make sure you have set up your notification settings in the .env file.
echo.
set /p confirm=Do you want to continue? (Y/N): 

if /i "%confirm%"=="Y" (
    echo.
    echo Sending test notifications...
    echo.
    curl -s http://localhost:5000/api/notifications/test
    echo.
    echo.
    echo If the server is not running, please start the server first (Option 1).
    echo.
) else (
    echo.
    echo Test cancelled.
    echo.
)
pause
goto MENU

:VIEW_DOCS
cls
echo Opening Documentation...
echo.
start ENHANCED_FEATURES.md
echo.
pause
goto MENU

:END
echo.
echo Thank you for using the USB Monitoring System!
echo.
exit /b 0
