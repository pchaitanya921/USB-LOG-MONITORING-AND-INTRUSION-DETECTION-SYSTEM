Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\USB Monitoring Dashboard.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\Users\chait\OneDrive\Desktop\USB LOG MONITORING AND INTRUSION DETECTION SYSTEM\simple-dashboard.html"
oLink.Description = "USB Monitoring Dashboard"
oLink.IconLocation = "C:\Windows\System32\shell32.dll,8"
oLink.Save
