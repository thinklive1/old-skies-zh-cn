param(
    [Parameter(Mandatory=$true)][string]$GameExe,
    [Parameter(Mandatory=$true)][string]$WorkDir,
    [string]$SdkVersion = '6.0.414',
    [string]$NuGetSource
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$taskWork = [System.IO.Path]::GetFullPath($WorkDir)
New-Item -ItemType Directory -Path $taskWork -Force | Out-Null
$upstream = Join-Path $taskWork 'AGSUnpacker'
$commit = '3971a5de79c8b45050ec8ddf742bec1a0bb6e2f5'
if (-not (Test-Path -LiteralPath $upstream)) {
    git -c http.sslBackend=openssl clone https://github.com/adm244/AGSUnpacker.git $upstream
    if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
    git -C $upstream checkout --detach $commit
    if ($LASTEXITCODE -ne 0) { throw 'Version pin failed' }
}
$actual = git -C $upstream rev-parse HEAD
if ($actual -ne $commit) { throw 'Upstream commit mismatch' }
$sdkSettings = @{ sdk = @{ version = $SdkVersion; rollForward = 'disable' } } | ConvertTo-Json
[System.IO.File]::WriteAllText((Join-Path $upstream 'global.json'), $sdkSettings)
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Extractor.cs') -Destination (Join-Path $upstream 'AGSUnpacker.CLI/Extractor.cs')
$program = 'namespace AGSUnpacker.CLI { class Program { static void Main(string[] args) { Extractor.Run(args[0], args[1]); } } }'
[System.IO.File]::WriteAllText((Join-Path $upstream 'AGSUnpacker.CLI/Program.cs'), $program)
$assets = Join-Path $taskWork 'assets'
python (Join-Path $PSScriptRoot 'extract_assets.py') $GameExe $assets
if ($LASTEXITCODE -ne 0) { throw 'Asset extraction failed' }
$env:DOTNET_CLI_HOME = Join-Path $taskWork 'dotnet-home'
$env:NUGET_PACKAGES = Join-Path $taskWork 'nuget-cache'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$buildArguments = @('build', (Join-Path $upstream 'AGSUnpacker.CLI/AGSUnpacker.CLI.csproj'), '-c', 'Release', '-o', (Join-Path $taskWork 'bin'), '--nologo')
if ($NuGetSource) { $buildArguments += @('--source', $NuGetSource) }
Push-Location -LiteralPath $upstream
try {
    dotnet @buildArguments
    if ($LASTEXITCODE -ne 0) { throw 'Extractor build failed' }
} finally { Pop-Location }
dotnet (Join-Path $taskWork 'bin/AGSUnpacker.CLI.dll') $assets (Join-Path $taskWork 'extracted.json')
if ($LASTEXITCODE -ne 0) { throw 'Text extraction failed' }
Write-Host ('Raw extraction: ' + (Join-Path $taskWork 'extracted.json'))
