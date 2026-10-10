<#
set-home-ip.ps1 -- M12 stage 3. Written by Claude, 2026-10-10.

Sets IIP_HOME_IP, for THIS PowerShell window only, to the home connection's
current public IPv4. dev.bicepparam reads it with readEnvironmentVariable(),
and main.bicep requires it at every networkStage (Gerard's choice), so run
this once in any new window before a what-if or deploy of main.bicep:

    cd C:\Users\gerar\geoste-portfolio\ai-103\infrastructure\iip
    .\set-home-ip.ps1

Why a live lookup and no stored value (Gerard, 2026-10-10): the address never
lands on disk, so this script can live in the public repo (D-M12-4), and if
Cox changes the address, the next run picks it up. A changed address shows up
in what-if as a change to stiipdevwus01's ipRules.

Why IPv4 only: stiipdevwus01 has only an A record, so the tower reaches it over
IPv4, whatever Entra's sign-in logs show (m12-prep.md, 2026-10-09). curl.exe -4
asks the lookup service over IPv4 for the same reason.

The address is printed so you can check it. Don't paste it, or any what-if
output that contains it, into a file in this repo.

Written for Windows PowerShell 5.1 and PowerShell 7 alike.
#>
$ErrorActionPreference = 'Stop'

$raw = & curl.exe -4 -s --max-time 10 https://api.ipify.org
if ($LASTEXITCODE -ne 0 -or -not $raw) {
    throw "Couldn't get the public IPv4 from api.ipify.org (curl exit code $LASTEXITCODE). IIP_HOME_IP is not set."
}
$ip = "$raw".Trim()

# Four numbers from 0 to 255 and nothing else: no CIDR suffix, no IPv6.
$isIpv4 = ($ip -match '^\d{1,3}(\.\d{1,3}){3}$') -and
          -not ($ip.Split('.') | Where-Object { [int]$_ -gt 255 })
if (-not $isIpv4) {
    throw "api.ipify.org returned '$ip', which isn't an IPv4 address. IIP_HOME_IP is not set."
}

$env:IIP_HOME_IP = $ip
Write-Host "IIP_HOME_IP set for this window: $ip"
