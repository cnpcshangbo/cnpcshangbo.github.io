# Offline source build/test helper. Never discovers, attaches to, or starts Minecraft.
[CmdletBinding()]
param(
    [string]$ClasspathFile,
    [string]$JdkBin = '',
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'local-build'),
    [switch]$TestOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$buildJava = if ($JdkBin) { Join-Path $JdkBin 'java.exe' } else { (Get-Command java -ErrorAction Stop).Source }
$buildJavac = if ($JdkBin) { Join-Path $JdkBin 'javac.exe' } else { (Get-Command javac -ErrorAction Stop).Source }
$buildJar = if ($JdkBin) { Join-Path $JdkBin 'jar.exe' } else { (Get-Command jar -ErrorAction Stop).Source }
$buildVersion = (& $buildJavac --version | Out-String)
if ($LASTEXITCODE -ne 0 -or $buildVersion -notmatch '^javac 25(?:\.|\s)') { throw 'Use a complete JDK 25 with java, javac and jar.' }
$buildJavaVersion = (& $buildJava --version | Out-String)
if ($LASTEXITCODE -ne 0 -or $buildJavaVersion -notmatch '(?m)^(?:openjdk|java) 25(?:\.|\s)') { throw 'java and javac must both be JDK 25.' }
$buildOutput = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $buildOutput) { throw 'Choose a fresh OutputDirectory. This helper does not delete or overwrite an existing build.' }
[IO.Directory]::CreateDirectory($buildOutput) | Out-Null
$buildTestClasses = Join-Path $buildOutput 'test-classes'
[IO.Directory]::CreateDirectory($buildTestClasses) | Out-Null
& $buildJavac --release 25 -encoding UTF-8 -d $buildTestClasses (Join-Path $PSScriptRoot 'src/woodagent/Navigation.java') (Join-Path $PSScriptRoot 'test/NavigationTest.java')
if ($LASTEXITCODE -ne 0) { throw 'Navigation test compilation failed.' }
& $buildJava -cp $buildTestClasses woodagent.NavigationTest
if ($LASTEXITCODE -ne 0) { throw 'Navigation tests failed.' }
if ($TestOnly) { Write-Output 'Pure Java navigation tests passed. No Minecraft dependency or connection was used.'; return }
if (-not $ClasspathFile) { throw 'Full build requires -ClasspathFile pointing to a private, locally supplied Minecraft 26.3-rc-2 runtime classpath.' }
$buildCp = [IO.File]::ReadAllText([IO.Path]::GetFullPath($ClasspathFile)).Trim()
$buildDependencies = $buildCp.Split([IO.Path]::PathSeparator)
if (-not ($buildDependencies -match '[\\/]versions[\\/]26\.3-rc-2[\\/]26\.3-rc-2\.jar$')) {
    throw 'Classpath must include the exact Minecraft 26.3-rc-2 client JAR at its standard versions location.'
}
foreach ($buildDependency in $buildDependencies) {
    if (-not [IO.File]::Exists($buildDependency)) { throw 'A supplied classpath entry does not exist. Inspect your private classpath file locally.' }
}
$buildClasses = Join-Path $buildOutput 'classes'
[IO.Directory]::CreateDirectory($buildClasses) | Out-Null
$buildSources = @((Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'src/woodagent') -Filter '*.java' -File | Sort-Object Name).FullName)
& $buildJavac --release 25 -encoding UTF-8 -cp $buildCp -d $buildClasses $buildSources
if ($LASTEXITCODE -ne 0) { throw 'Worker compilation failed; this source targets Minecraft 26.3-rc-2 only.' }
$buildJarPath = Join-Path $buildOutput 'wood-agent.jar'
& $buildJar --create --file $buildJarPath --manifest (Join-Path $PSScriptRoot 'manifest.mf') --date=2026-09-13T00:00:00Z -C $buildClasses .
if ($LASTEXITCODE -ne 0) { throw 'Agent JAR packaging failed.' }
Write-Output "Built $buildJarPath"
Write-Output 'No controller was attached or started. Keep the private classpath file out of public artifacts.'
