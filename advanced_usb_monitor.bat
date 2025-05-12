@echo off
echo USB Monitoring System - Advanced Edition
echo ======================================
echo.

:MENU
cls
echo USB Monitoring System - Advanced Edition
echo ======================================
echo.
echo Choose an option:
echo 1. Start USB Monitoring System (Web Interface)
echo 2. Start System Tray Application
echo 3. Install YARA for Enhanced Malware Detection
echo 4. Set Up Automatic Startup (Web Interface)
echo 5. Set Up Automatic Startup (System Tray)
echo 6. Test Notifications
echo 7. View Documentation
echo 8. Exit
echo.

set /p choice=Enter your choice (1-8): 

if "%choice%"=="1" goto START_WEB
if "%choice%"=="2" goto START_TRAY
if "%choice%"=="3" goto INSTALL_YARA
if "%choice%"=="4" goto SETUP_AUTOSTART_WEB
if "%choice%"=="5" goto SETUP_AUTOSTART_TRAY
if "%choice%"=="6" goto TEST_NOTIFICATIONS
if "%choice%"=="7" goto VIEW_DOCS
if "%choice%"=="8" goto END

echo Invalid choice. Please try again.
echo.
pause
goto MENU

:START_WEB
cls
echo Starting USB Monitoring System (Web Interface)...
echo.
echo The web interface will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.
start http://localhost:5000
python clean_app.py
goto MENU

:START_TRAY
cls
echo Starting USB Monitoring System (System Tray)...
echo.
call run_system_tray.bat
goto MENU

:INSTALL_YARA
cls
echo Installing YARA for Enhanced Malware Detection...
echo.
call install_yara.bat
echo.
pause
goto MENU

:SETUP_AUTOSTART_WEB
cls
echo Setting Up Automatic Startup (Web Interface)...
echo.
call setup_autostart.bat
echo.
pause
goto MENU

:SETUP_AUTOSTART_TRAY
cls
echo Setting Up Automatic Startup (System Tray)...
echo.
call setup_tray_autostart.bat
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
echo Choose documentation to view:
echo 1. Basic Features
echo 2. Enhanced Features
echo 3. Advanced Features
echo 4. Back to Main Menu
echo.

set /p doc_choice=Enter your choice (1-4): 

if "%doc_choice%"=="1" (
    start README.md
) else if "%doc_choice%"=="2" (
    start ENHANCED_FEATURES.md
) else if "%doc_choice%"=="3" (
    start ADVANCED_FEATURES.md
) else if "%doc_choice%"=="4" (
    goto MENU
) else (
    echo Invalid choice.
)
echo.
pause
goto MENU

:END
echo.
echo Thank you for using the USB Monitoring System!
echo.
exit /b 0
