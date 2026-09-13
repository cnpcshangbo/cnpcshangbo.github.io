[CmdletBinding()]
param([Parameter(Mandatory)][string]$AgentDirectory, [Parameter(Mandatory)][string]$RunId)
. (Join-Path $PSScriptRoot 'common.ps1')
$woodRuntime = Get-WoodRuntime $AgentDirectory
$woodReason = 'Watchdog interrupted'
$woodShouldStop = $true
try {
    $woodSession = Read-WoodJson (Join-Path $woodRuntime 'session.json')
    if ($null -eq $woodSession -or $woodSession.runId -ne $RunId) { $woodShouldStop=$false; return }
    $woodDeadline = ConvertTo-WoodInstant $woodSession.deadline
    # Never trust a modified session file to extend the twenty-minute bound.
    $woodHardDeadline = (ConvertTo-WoodInstant $woodSession.startedAt).AddMinutes(20)
    if ($woodDeadline -gt $woodHardDeadline) { $woodDeadline = $woodHardDeadline }
    while ($true) {
        $woodCurrent = Read-WoodJson (Join-Path $woodRuntime 'session.json')
        $woodCommand = Read-WoodJson (Join-Path $woodRuntime 'command.json')
        if ($null -eq $woodCurrent -or $woodCurrent.runId -ne $RunId -or $null -eq $woodCommand -or $woodCommand.id -ne $RunId) {
            $woodReason='A newer command or session took over'; $woodShouldStop=$false; break
        }
        if (-not (Test-WoodProcess $woodSession.processId $woodSession.processStartTicks)) { $woodReason='Minecraft exited'; break }
        if ([DateTimeOffset]::UtcNow -ge $woodDeadline) { $woodReason='Twenty-minute watchdog limit'; break }
        $woodState = Read-WoodJson (Join-Path $woodRuntime 'status.json')
        if ((Get-WoodAge $woodState) -gt 15) { $woodReason='Controller status became stale'; break }
        if ($woodState.commandId -eq $RunId) {
            if (-not $woodState.active) { $woodReason="Controller ended: $($woodState.phase)"; $woodShouldStop=$false; break }
            Update-WoodLease $woodRuntime
        } elseif (([DateTimeOffset]::UtcNow - (ConvertTo-WoodInstant $woodSession.startedAt)).TotalSeconds -gt 10) {
            $woodReason='Start command was not acknowledged'; break
        }
        $woodWaitMs = [Math]::Max(1, [Math]::Min(3000, [Math]::Floor(($woodDeadline - [DateTimeOffset]::UtcNow).TotalMilliseconds)))
        Start-Sleep -Milliseconds ([int]$woodWaitMs)
    }
} catch {
    $woodReason='Watchdog error: ' + $_.Exception.Message
} finally {
    if ($woodShouldStop) { try { Stop-WoodRun $woodRuntime $RunId | Out-Null } catch {} }
    try {
        $woodCurrent = Read-WoodJson (Join-Path $woodRuntime 'session.json')
        if ($null -ne $woodCurrent -and $woodCurrent.runId -eq $RunId) {
            Write-WoodJson (Join-Path $woodRuntime 'watchdog.json') @{ runId=$RunId; endedAt=[DateTimeOffset]::UtcNow.ToString('o'); reason=$woodReason }
        }
    } catch {}
}
