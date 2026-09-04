# md-to-docx Explorer context-menu runner.
# Usage: runner.ps1 convert|reverse <file> [file...]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("convert", "reverse")]
    [string]$Action,

    [Parameter(Mandatory = $true, Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Files
)

$ErrorActionPreference = "Stop"

$ConfDir = Join-Path $env:LOCALAPPDATA "md-to-docx"
$ConfFile = Join-Path $ConfDir "context-menu.conf"

function Show-Notify {
    param([string]$Title, [string]$Message, [string]$Icon = "Information")
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        [System.Windows.Forms.MessageBox]::Show($Message, $Title, "OK", $Icon) | Out-Null
    } catch {
        Write-Host "${Title}: ${Message}"
    }
}

function Read-Conf {
    $cli = $env:MD_TO_DOCX_CLI
    $preset = ""
    $extraArgs = @()

    if (Test-Path -LiteralPath $ConfFile) {
        Get-Content -LiteralPath $ConfFile | ForEach-Object {
            $line = $_.Trim()
            if ($line -match '^\s*#' -or $line -eq "") { return }
            if ($line -match '^CLI=(.*)$') {
                $val = $Matches[1].Trim().Trim('"')
                if (-not $cli) { $cli = $val }
            } elseif ($line -match '^PRESET=(.*)$') {
                $preset = $Matches[1].Trim().Trim('"')
            } elseif ($line -match '^EXTRA_ARGS=(.*)$') {
                $raw = $Matches[1].Trim().Trim('"')
                if ($raw) {
                    $extraArgs = $raw -split '\s+' | Where-Object { $_ }
                }
            }
        }
    }

    if (-not $cli) {
        Show-Notify "md-to-docx" "CLI path missing. Re-run desktop/windows/install.ps1 or set MD_TO_DOCX_CLI." "Error"
        exit 1
    }
    if (-not (Test-Path -LiteralPath $cli)) {
        # Allow bare command name on PATH
        $cmd = Get-Command $cli -ErrorAction SilentlyContinue
        if (-not $cmd) {
            Show-Notify "md-to-docx" "CLI not found: $cli. Re-run install or set MD_TO_DOCX_CLI." "Error"
            exit 1
        }
        $cli = $cmd.Source
    }

    return @{
        Cli = $cli
        Preset = $preset
        ExtraArgs = $extraArgs
    }
}

$cfg = Read-Conf
$ok = 0
$fail = 0
$failNames = New-Object System.Collections.Generic.List[string]

foreach ($f in $Files) {
    if (-not $f) { continue }
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) {
        $fail++
        $failNames.Add("$(Split-Path $f -Leaf) (missing)")
        continue
    }

    $base = Split-Path $f -Leaf
    $ext = [System.IO.Path]::GetExtension($f).TrimStart(".").ToLowerInvariant()

    try {
        if ($Action -eq "convert") {
            if ($ext -notin @("md", "markdown")) {
                $fail++
                $failNames.Add("$base (not .md)")
                continue
            }
            if ($cfg.Preset) {
                $argList = @($f, "--preset", $cfg.Preset) + $cfg.ExtraArgs
            } else {
                $argList = @($f) + $cfg.ExtraArgs
            }
            & $cfg.Cli @argList
            if ($LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
            $ok++
        } else {
            if ($ext -ne "docx") {
                $fail++
                $failNames.Add("$base (not .docx)")
                continue
            }
            & $cfg.Cli reverse $f
            if ($LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
            $ok++
        }
    } catch {
        $fail++
        $failNames.Add($base)
    }
}

if ($fail -eq 0) {
    if ($Action -eq "convert") {
        # Success: silent balloon-style short message via MessageBox is noisy;
        # use a brief Information box only when converting multiple files.
        if ($ok -gt 1) {
            Show-Notify "md-to-docx" "Converted $ok file(s) to Word"
        }
        exit 0
    }
    if ($ok -gt 1) {
        Show-Notify "md-to-docx" "Reversed $ok file(s) to Markdown"
    }
    exit 0
}

$summary = "ok=$ok fail=$fail"
if ($failNames.Count -gt 0) {
    $summary = "${summary}: $($failNames -join ', ')"
}
Show-Notify "md-to-docx failed" $summary "Error"
exit 1
