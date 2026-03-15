# setup.ps1 — twitch_viewer first-time setup
# Copies tw.bat to your home directory so you can launch via Win+R
# Also sets up config.py from the example template if not already present
#
# Usage: right-click setup.ps1 -> "Run with PowerShell"
#   or:  pwsh -ExecutionPolicy Bypass -File setup.ps1

$repoDir = $PSScriptRoot
$homeDir = $env:USERPROFILE

Write-Host ""
Write-Host "  twitch_viewer setup" -ForegroundColor Cyan
Write-Host "  ===================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: config.py ---
$configDest = Join-Path $repoDir "config.py"
$configExample = Join-Path $repoDir "config.example.py"

if (Test-Path $configDest) {
    Write-Host "  [ok] config.py already exists - skipping" -ForegroundColor Green
} else {
    Copy-Item $configExample $configDest
    Write-Host "  [ok] Created config.py from config.example.py" -ForegroundColor Green
    Write-Host "  [!!] Open config.py and fill in your CLIENT_ID, BEARER_TOKEN, and USER_ID" -ForegroundColor Yellow
    Write-Host "       https://dev.twitch.tv/console" -ForegroundColor DarkGray
}

Write-Host ""

# --- Step 2: tw.bat -> home dir ---
$twSrc  = Join-Path $repoDir "tw.bat"
$twDest = Join-Path $homeDir "tw.bat"

# Generate a tw.bat that points to THIS repo location
$twContent = "@echo off`npython `"$repoDir\twitch.py`" %*`nif %ERRORLEVEL% neq 0 (`n    echo ERROR: twitch.py failed with error code %ERRORLEVEL%`n    pause`n    exit /b %ERRORLEVEL%`n)"

Set-Content -Path $twDest -Value $twContent -Encoding ASCII

Write-Host "  [ok] Installed tw.bat to $homeDir" -ForegroundColor Green
Write-Host "       You can now run 'tw' from Win+R" -ForegroundColor DarkGray

Write-Host ""

# --- Step 3: Verify dependencies ---
Write-Host "  Checking dependencies..." -ForegroundColor Cyan
Write-Host ""

$checks = @(
    @{ Name = "Python";     Cmd = "python --version" },
    @{ Name = "Streamlink"; Cmd = "streamlink --version" },
    @{ Name = "colorama";   Cmd = "python -c `"import colorama`"" },
    @{ Name = "requests";   Cmd = "python -c `"import requests`"" }
)

$allGood = $true
foreach ($check in $checks) {
    try {
        $out = Invoke-Expression $check.Cmd 2>&1
        Write-Host "  [ok] $($check.Name)" -ForegroundColor Green
    } catch {
        Write-Host "  [!!] $($check.Name) not found" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""

if ($allGood) {
    Write-Host "  All dependencies found. You're good to go!" -ForegroundColor Green
    Write-Host "  Run 'tw' from Win+R to launch." -ForegroundColor Cyan
} else {
    Write-Host "  Some dependencies are missing. See README.md for install instructions." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
