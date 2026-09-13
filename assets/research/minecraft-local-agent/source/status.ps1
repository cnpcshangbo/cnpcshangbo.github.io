[CmdletBinding()]
param([switch]$RenewLease, [string]$AgentDirectory = $PSScriptRoot)
. (Join-Path $PSScriptRoot 'common.ps1')
$woodRuntime = Get-WoodRuntime $AgentDirectory
$woodState = Read-WoodJson (Join-Path $woodRuntime 'status.json')
if ($null -eq $woodState) { throw 'No controller status exists. Run start.ps1 first.' }
$woodAge = Get-WoodAge $woodState
if ($RenewLease) {
    $woodCommand = Read-WoodJson (Join-Path $woodRuntime 'command.json')
    if ($woodAge -gt 15 -or -not $woodState.active -or $null -eq $woodCommand -or $woodCommand.id -ne $woodState.commandId -or $woodCommand.action -notin @('start','resume')) {
        throw 'Lease renewal requires a fresh, active run with its original start or resume command still current.'
    }
    Update-WoodLease $woodRuntime
}
$woodState | Add-Member -NotePropertyName statusAgeSeconds -NotePropertyValue ([Math]::Round($woodAge,1)) -Force
$woodState | ConvertTo-Json -Depth 12
if ($woodAge -gt 15) { Write-Warning 'Status is stale; the controller may be unavailable.'; exit 2 }
