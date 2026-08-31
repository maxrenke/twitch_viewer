# setup.ps1 — twitch_viewer first-time setup
# Installs a forwarding shim for every Win+R-launched script into your home
# directory (Win+R runs through Explorer, which only sees things on PATH or
# physically in %USERPROFILE% - the repo folder alone isn't enough).
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

# --- Step 2: Win+R shims -> home dir ---
# tw.bat forwards to twitch.py directly (it's the only one that needs a real
# python invocation, not just a re-dispatch); everything else is a thin
# `call`/`Run` forward to the repo copy so there is one source of truth.

$twContent = "@echo off`npython `"$repoDir\twitch.py`" %*`nif %ERRORLEVEL% neq 0 (`n    echo ERROR: twitch.py failed with error code %ERRORLEVEL%`n    pause`n    exit /b %ERRORLEVEL%`n)"
Set-Content -Path (Join-Path $homeDir "tw.bat") -Value $twContent -Encoding ASCII

$batShims = "kick.bat", "live.bat", "lsh.bat", "lsh_optimized_configs.bat", "lshk.bat", "kickplay.bat"
foreach ($name in $batShims) {
    $content = "@echo off`ncall `"$repoDir\$name`" %*"
    Set-Content -Path (Join-Path $homeDir $name) -Value $content -Encoding ASCII
}

$vbsShims = "ls.vbs", "ls_optimized.vbs", "lsk.vbs", "kick.vbs"
foreach ($name in $vbsShims) {
    $target = "$repoDir\$name"
    $content = "' Forwarding shim: real script lives in $target`n" +
        "Dim WshShell, target, args, i`n" +
        "Set WshShell = CreateObject(`"WScript.Shell`")`n" +
        "target = `"$target`"`n" +
        "args = `"`"`n" +
        "For i = 0 To WScript.Arguments.Count - 1`n" +
        "    args = args & `" `" & Chr(34) & WScript.Arguments(i) & Chr(34)`n" +
        "Next`n" +
        "WshShell.Run Chr(34) & target & Chr(34) & args, 0, True`n" +
        "Set WshShell = Nothing`n"
    Set-Content -Path (Join-Path $homeDir $name) -Value $content -Encoding ASCII
}

Write-Host "  [ok] Installed $($batShims.Count + $vbsShims.Count + 1) Win+R shims to $homeDir" -ForegroundColor Green
Write-Host "       tw, kick, live, lsh, lsh_optimized_configs, lshk, kickplay, ls, ls_optimized, lsk, kick(.vbs)" -ForegroundColor DarkGray

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
