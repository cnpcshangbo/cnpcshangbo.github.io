[CmdletBinding()]
param(
    [ValidateRange(1,64)][int]$Logs = 32,
    [ValidateRange(128,512)][double]$Radius = 128,
    [double]$HomeX = -698,
    [double]$HomeZ = 195,
    [ValidateRange(0,60)][int]$DelaySeconds = 3,
    [int]$MinecraftProcessId = 0,
    [switch]$Resume,
    [switch]$NoWatchdog,
    [string]$AgentDirectory = $PSScriptRoot
)
. (Join-Path $PSScriptRoot 'common.ps1')

$woodDirectory = [IO.Path]::GetFullPath($AgentDirectory)
$woodRuntime = Get-WoodRuntime $woodDirectory
if ($Resume) {
    foreach ($woodOption in @('Logs','Radius','HomeX','HomeZ')) {
        if ($PSBoundParameters.ContainsKey($woodOption)) { throw '-Resume uses the saved mission settings; omit Logs, Radius, HomeX, and HomeZ.' }
    }
    $woodMission = Read-WoodMission $woodRuntime
    $Logs = [int]$woodMission.targetLogs; $Radius = [double]$woodMission.radius
    $HomeX = [double]$woodMission.homeX; $HomeZ = [double]$woodMission.homeZ
}
foreach ($woodCoordinate in @($HomeX,$HomeZ,$Radius)) {
    if ([double]::IsNaN($woodCoordinate) -or [double]::IsInfinity($woodCoordinate) -or [Math]::Abs($woodCoordinate) -gt 29999984) {
        throw 'Home coordinates and radius must be finite values inside the world border.'
    }
}
$woodJar = Join-Path $woodDirectory 'wood-agent.jar'
if (-not [IO.File]::Exists($woodJar)) { throw 'wood-agent.jar must be beside these scripts.' }
$woodLock = $null
$woodStartedId = ''
try {
    $woodLock = [IO.File]::Open((Join-Path $woodRuntime 'launcher.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    $woodOld = Read-WoodJson (Join-Path $woodRuntime 'status.json')
    if ($null -ne $woodOld -and $woodOld.active -and (Get-WoodAge $woodOld) -lt 10) {
        throw 'This package already has an active run. Use stop.ps1 and wait for its acknowledgment first.'
    }
    $woodClient = Find-WoodClient $MinecraftProcessId
    $woodVersion = (& $woodClient.Java --version | Out-String)
    if ($LASTEXITCODE -ne 0 -or $woodVersion -notmatch '(?m)^(?:openjdk|java) 25(?:\.|\s)') { throw 'This package requires the Minecraft bundled Java 25 runtime.' }
    $woodModules = & $woodClient.Java --list-modules
    if ($LASTEXITCODE -ne 0 -or -not ($woodModules -match '^jdk.attach@')) { throw 'The bundled Java runtime has no jdk.attach module.' }

    $woodAttachTime = [DateTimeOffset]::UtcNow
    & $woodClient.Java --add-modules jdk.attach -cp $woodJar woodagent.Attach ([string]$woodClient.ProcessId) $woodDirectory
    if ($LASTEXITCODE -ne 0) { throw 'The idle controller did not attach. No start command was sent.' }
    $woodReady = $false
    for ($woodAttempt = 0; $woodAttempt -lt 40; $woodAttempt++) {
        Start-Sleep -Milliseconds 250
        $woodState = Read-WoodJson (Join-Path $woodRuntime 'status.json')
        if ($null -ne $woodState -and (ConvertTo-WoodInstant $woodState.updatedAt) -ge $woodAttachTime -and $woodState.phase -eq 'IDLE' -and -not $woodState.active) {
            $woodReady = $true; break
        }
    }
    if (-not $woodReady) { throw 'The attached controller has not published fresh idle status. No start command was sent.' }

    if ($Resume) { Write-Host "Resuming the saved mission: target $Logs logs outside radius $Radius around X=$HomeX, Z=$HomeZ; original return path and inventory baseline retained." }
    else { Write-Host "Aiming for $Logs new logs outside radius $Radius around X=$HomeX, Z=$HomeZ." }
    Write-Host "Starting in $DelaySeconds seconds; press Ctrl+C now to cancel. Minecraft can remain unfocused."
    if ($DelaySeconds -gt 0) { Start-Sleep -Seconds $DelaySeconds }
    if (-not (Test-WoodProcess $woodClient.ProcessId $woodClient.StartTicks)) { throw 'The selected Minecraft process exited.' }
    $woodStartedId = [Guid]::NewGuid().ToString()
    $woodStartTime = [DateTimeOffset]::UtcNow
    Write-WoodJson (Join-Path $woodRuntime 'session.json') @{
        runId = $woodStartedId; processId = $woodClient.ProcessId; processStartTicks = $woodClient.StartTicks
        startedAt = $woodStartTime.ToString('o'); deadline = $woodStartTime.AddMinutes(20).AddSeconds(-1).ToString('o')
        watchdog = (-not $NoWatchdog.IsPresent)
    }
    Update-WoodLease $woodRuntime
    Write-WoodJson (Join-Path $woodRuntime 'command.json') @{
        id = $woodStartedId; action = $(if ($Resume) { 'resume' } else { 'start' }); logs = $Logs; radius = $Radius; homeX = $HomeX; homeZ = $HomeZ
    }
    if (-not $NoWatchdog) {
        $woodShell = Join-Path $PSHOME 'pwsh.exe'
        if (-not [IO.File]::Exists($woodShell)) { $woodShell = Join-Path $PSHOME 'powershell.exe' }
        $woodWatchScript = Join-Path $PSScriptRoot 'watchdog.ps1'
        $woodCode = "& '" + $woodWatchScript.Replace("'", "''") + "' -AgentDirectory '" + $woodDirectory.Replace("'", "''") + "' -RunId '" + $woodStartedId + "'"
        $woodEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($woodCode))
        $woodWatch = Start-Process -FilePath $woodShell -ArgumentList @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-EncodedCommand',$woodEncoded) -WindowStyle Hidden -PassThru
        Write-Host "Local watchdog started (PID $($woodWatch.Id)); maximum run time is 20 minutes."
    } else {
        Write-Host 'No watchdog: renew the lease with status.ps1 -RenewLease at least once per minute.'
    }
    for ($woodAttempt = 0; $woodAttempt -lt 40; $woodAttempt++) {
        Start-Sleep -Milliseconds 250
        $woodState = Read-WoodJson (Join-Path $woodRuntime 'status.json')
        if ($null -ne $woodState -and $woodState.commandId -eq $woodStartedId) {
            if (-not $woodState.active) { throw "Controller did not remain active: $($woodState.reason)" }
            Write-Host "Running: $($woodState.phase). Use status.ps1 to inspect or stop.ps1 to stop."
            return
        }
    }
    throw 'No start acknowledgment arrived within 10 seconds.'
} catch {
    if ($woodStartedId) { Stop-WoodRun $woodRuntime $woodStartedId | Out-Null }
    throw
} finally {
    if ($null -ne $woodLock) { $woodLock.Dispose() }
}

