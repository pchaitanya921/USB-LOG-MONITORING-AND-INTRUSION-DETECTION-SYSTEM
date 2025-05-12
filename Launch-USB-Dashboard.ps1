# PowerShell script to launch the USB Monitoring Dashboard
Write-Host "Launching USB Monitoring Dashboard..." -ForegroundColor Cyan

# Path to the dashboard HTML file
$dashboardPath = "C:\Users\chait\OneDrive\Desktop\USB LOG MONITORING AND INTRUSION DETECTION SYSTEM\simple-dashboard.html"

# Launch the dashboard in the default browser
Start-Process $dashboardPath

Write-Host "Dashboard launched successfully!" -ForegroundColor Green
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
