# IronWall Antivirus PowerShell Launcher
# Run with: powershell -ExecutionPolicy Bypass -File run_ironwall.ps1

param(
    [switch]$Admin,
    [switch]$Help
)

function Show-Help {
    Write-Host @"
IronWall Antivirus PowerShell Launcher

Usage:
    .\run_ironwall.ps1                    # Run normally
    .\run_ironwall.ps1 -Admin             # Run with admin privileges
    .\run_ironwall.ps1 -Help              # Show this help

Options:
    -Admin    Request administrator privileges
    -Help     Show this help message

Examples:
    .\run_ironwall.ps1                    # Normal launch
    .\run_ironwall.ps1 -Admin             # Launch as administrator
"@
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Request-AdminPrivileges {
    if (-not (Test-AdminPrivileges)) {
        Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
        $arguments = "& '$PSCommandPath'"
        Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -Command $arguments"
        exit
    }
}

# Show help if requested
if ($Help) {
    Show-Help
    exit 0
}

# Request admin privileges if needed
if ($Admin) {
    Request-AdminPrivileges
}

Write-Host "🛡️  IronWall Antivirus - PowerShell Launcher" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ ERROR: main.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the IronWall directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import psutil, tkinter" 2>$null
    Write-Host "✅ All dependencies are installed" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing missing dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check admin privileges
if (Test-AdminPrivileges) {
    Write-Host "🔐 Running with administrator privileges" -ForegroundColor Green
} else {
    Write-Host "⚠️  Running without administrator privileges" -ForegroundColor Yellow
    Write-Host "   Some features may be limited" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting IronWall Antivirus..." -ForegroundColor Green
Write-Host ""

# Run IronWall
try {
    python main.py
    Write-Host ""
    Write-Host "✅ IronWall Antivirus has been closed." -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to start IronWall" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Read-Host "Press Enter to exit" 