[CmdletBinding()]
param([string]$AgentDirectory = $PSScriptRoot)
. (Join-Path $PSScriptRoot 'common.ps1')
$woodRuntime = Get-WoodRuntime $AgentDirectory
$woodStopId = Stop-WoodRun $woodRuntime
for ($woodAttempt = 0; $woodAttempt -lt 40; $woodAttempt++) {
    Start-Sleep -Milliseconds 250
    $woodState = Read-WoodJson (Join-Path $woodRuntime 'status.json')
    if ($null -ne $woodState -and $woodState.commandId -eq $woodStopId -and -not $woodState.active) {
        Write-Host "Stopped: $($woodState.reason)"
        return
    }
}
Write-Warning 'Stop was requested, but the game has not acknowledged it. Focus Minecraft and press Escape. No further lease renewal was requested.'
exit 2
