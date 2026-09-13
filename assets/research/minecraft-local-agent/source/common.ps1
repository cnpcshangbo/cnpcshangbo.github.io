Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-WoodRuntime([string]$Directory) {
    $woodPath = Join-Path ([IO.Path]::GetFullPath($Directory)) 'runtime'
    [IO.Directory]::CreateDirectory($woodPath) | Out-Null
    return $woodPath
}

function Read-WoodJson([string]$Path) {
    if (-not [IO.File]::Exists($Path)) { return $null }
    return [IO.File]::ReadAllText($Path) | ConvertFrom-Json
}

function Read-WoodMission([string]$Runtime) {
    $woodSaved = Read-WoodJson (Join-Path $Runtime 'mission.json')
    if ($null -eq $woodSaved) { throw 'No saved mission exists at runtime/mission.json. Resume requires the original mission file.' }
    foreach ($woodField in @('homeX','homeZ','radius','targetLogs','baselineLogs','start','breadcrumbs')) {
        if ($woodSaved.PSObject.Properties.Name -notcontains $woodField) { throw "Saved mission is missing $woodField." }
    }
    foreach ($woodCoordinate in @([double]$woodSaved.homeX,[double]$woodSaved.homeZ,[double]$woodSaved.radius)) {
        if ([double]::IsNaN($woodCoordinate) -or [double]::IsInfinity($woodCoordinate) -or [Math]::Abs($woodCoordinate) -gt 29999984) {
            throw 'Saved mission coordinates must be finite values inside the world border.'
        }
    }
    if ($woodSaved.radius -lt 128 -or $woodSaved.radius -gt 512 -or $woodSaved.targetLogs -lt 1 -or $woodSaved.targetLogs -gt 64 -or
        [double]$woodSaved.targetLogs -ne [Math]::Floor([double]$woodSaved.targetLogs) -or $woodSaved.baselineLogs -lt 0 -or $woodSaved.baselineLogs -gt 2304 -or
        [double]$woodSaved.baselineLogs -ne [Math]::Floor([double]$woodSaved.baselineLogs)) { throw 'Saved mission limits are invalid.' }
    if (@($woodSaved.breadcrumbs).Count -lt 1 -or @($woodSaved.breadcrumbs).Count -gt 20000) { throw 'Saved mission has no usable return path.' }
    foreach ($woodPoint in @($woodSaved.start) + @($woodSaved.breadcrumbs)) {
        foreach ($woodAxis in @('x','y','z')) {
            if ($null -eq $woodPoint -or $woodPoint.PSObject.Properties.Name -notcontains $woodAxis) { throw 'Saved mission contains an incomplete path coordinate.' }
            $woodValue = [double]$woodPoint.$woodAxis
            if ([double]::IsNaN($woodValue) -or [double]::IsInfinity($woodValue) -or [Math]::Abs($woodValue) -gt 29999984 -or $woodValue -ne [Math]::Floor($woodValue)) {
                throw 'Saved mission path coordinates must be finite integer block positions.'
            }
        }
    }
    return $woodSaved
}

function Write-WoodJson([string]$Path, $Value) {
    $woodTemp = $Path + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    $woodBackup = $woodTemp + '.bak'
    try {
        [IO.File]::WriteAllText($woodTemp, ($Value | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
        if ([IO.File]::Exists($Path)) { [IO.File]::Replace($woodTemp, $Path, $woodBackup) }
        else { [IO.File]::Move($woodTemp, $Path) }
    } finally {
        if ([IO.File]::Exists($woodTemp)) { [IO.File]::Delete($woodTemp) }
        if ([IO.File]::Exists($woodBackup)) { [IO.File]::Delete($woodBackup) }
    }
}

function ConvertTo-WoodInstant($Value) {
    # PowerShell 7.5 may parse JSON dates as DateTime; Java emits a trailing Z.
    # Preserve DateTime.Kind rather than formatting UTC as an unlabeled local time.
    if ($Value -is [DateTimeOffset]) { return $Value }
    if ($Value -is [DateTime]) { return [DateTimeOffset]::new($Value) }
    return [DateTimeOffset]::Parse([string]$Value, [Globalization.CultureInfo]::InvariantCulture)
}

function Get-WoodAge($Status) {
    if ($null -eq $Status -or -not $Status.updatedAt) { return [double]::PositiveInfinity }
    return ([DateTimeOffset]::UtcNow - (ConvertTo-WoodInstant $Status.updatedAt)).TotalSeconds
}

function Update-WoodLease([string]$Runtime) {
    [IO.File]::WriteAllText((Join-Path $Runtime 'lease'), [DateTimeOffset]::UtcNow.ToString('o'))
}

function Stop-WoodRun([string]$Runtime, [string]$ExpectedRunId = '') {
    if ($ExpectedRunId) {
        $woodCommand = Read-WoodJson (Join-Path $Runtime 'command.json')
        if ($null -eq $woodCommand -or $woodCommand.id -ne $ExpectedRunId) { return $null }
    }
    $woodId = [Guid]::NewGuid().ToString()
    Write-WoodJson (Join-Path $Runtime 'command.json') @{ id = $woodId; action = 'stop' }
    return $woodId
}

function Find-WoodClient([int]$RequestedProcessId = 0) {
    $woodMatches = @(
        Get-CimInstance Win32_Process -Filter "Name = 'javaw.exe' OR Name = 'java.exe'" | Where-Object {
            # Inspect the command line in memory only. Never print it: it can contain login tokens.
            $_.CommandLine -match '(?:^|\s)net\.minecraft\.client\.main\.Main(?:\s|$)' -and
            $_.CommandLine -match '(?:^|\s)--version\s+"?26\.3-rc-2"?(?:\s|$)' -and
            ($RequestedProcessId -eq 0 -or $_.ProcessId -eq $RequestedProcessId)
        }
    )
    if ($woodMatches.Count -ne 1) {
        throw "Expected one running Minecraft Java 26.3-rc-2 client; found $($woodMatches.Count). Use -MinecraftProcessId when several are open."
    }
    $woodProcess = $woodMatches[0]
    if ($woodProcess.CommandLine -match '(?:-XX:\+DisableAttachMechanism|-XX:-EnableDynamicAgentLoading)') {
        throw 'This Minecraft process disables Java agent loading.'
    }
    $woodJava = Join-Path (Split-Path -Parent $woodProcess.ExecutablePath) 'java.exe'
    if (-not [IO.File]::Exists($woodJava)) { throw 'The running client Java executable could not be resolved.' }
    $woodIdentity = (Get-Process -Id $woodProcess.ProcessId).StartTime.ToUniversalTime().Ticks.ToString()
    # Return only the safe fields required by the launcher and watchdog.
    return [pscustomobject]@{ ProcessId = [int]$woodProcess.ProcessId; Java = $woodJava; StartTicks = $woodIdentity }
}

function Test-WoodProcess([int]$ProcessId, [string]$StartTicks) {
    $woodProcess = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    return $null -ne $woodProcess -and $woodProcess.StartTime.ToUniversalTime().Ticks.ToString() -eq $StartTicks
}
