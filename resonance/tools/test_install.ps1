param([string]$WorkRoot)
$ErrorActionPreference='Stop'
$Project=Split-Path $PSScriptRoot -Parent
$Package=Join-Path $Project 'build\Resonance_简体中文汉化_v1.1_全量校对候选版'
$ReportName='installer_tests.json'
if ($env:RESONANCE_TEST_PACKAGE) { $Package=[IO.Path]::GetFullPath($env:RESONANCE_TEST_PACKAGE);$ReportName='installer_tests_final_zip.json' }
$Old=Join-Path $Project 'baseline\v1.0.1'
if (-not $WorkRoot) { throw 'WorkRoot required: use a dedicated fixture directory.' }
$WorkRoot=[IO.Path]::GetFullPath($WorkRoot)
if (Test-Path -LiteralPath $WorkRoot) { throw 'Fixture directory must be new.' }
New-Item -ItemType Directory -Path $WorkRoot | Out-Null
$Results=New-Object Collections.Generic.List[object]
function Hash([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Assert([bool]$Condition,[string]$Message) { if (-not $Condition) { throw $Message } }
function RunScript([string]$Root,[string]$Entry,[string]$Game,[bool]$Success,[string]$Label) {
    $log=Join-Path $WorkRoot ($Label+'.log')
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File (Join-Path $Root $Entry) -GameDir $Game *> $log
    $code=$LASTEXITCODE
    Assert (($Success -and $code -eq 0) -or ((-not $Success) -and $code -ne 0)) ("$Label exit $code; inspect $log")
    $Results.Add([ordered]@{test=$Label;passed=$true;expected_success=$Success;exit_code=$code;log=(Split-Path $log -Leaf)})
}
function Fixture([string]$Name) {
    $d=Join-Path $WorkRoot $Name;New-Item -ItemType Directory -Path $d | Out-Null
    # A syntactically valid PE header for installer checks, never executed.
    $b=New-Object byte[] 4096;$b[0]=77;$b[1]=90
    [BitConverter]::GetBytes([int]128).CopyTo($b,60)
    [BitConverter]::GetBytes([int]17744).CopyTo($b,128)
    [BitConverter]::GetBytes([uint16]332).CopyTo($b,132)
    [BitConverter]::GetBytes([uint16]1).CopyTo($b,134)
    [BitConverter]::GetBytes([uint16]224).CopyTo($b,148)
    [BitConverter]::GetBytes([uint16]267).CopyTo($b,152)
    [IO.File]::WriteAllBytes((Join-Path $d 'Resonance.exe'),$b)
    [IO.File]::WriteAllText((Join-Path $d 'acsetup.cfg'),"[misc]`r`nwindowed=1`r`n[language]`r`ntranslation=English`r`n",(New-Object Text.UTF8Encoding($false)))
    [IO.File]::WriteAllText((Join-Path $d 'Chinese.tra'),'PREEXISTING TRANSLATION')
    [IO.File]::WriteAllText((Join-Path $d 'player-save.sav'),'SENTINEL SAVE: MUST STAY IDENTICAL')
    return $d
}
foreach($p in Get-ChildItem -LiteralPath $Package -Filter '*.ps1' -File) {
    $tokens=$null;$errors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($p.FullName,[ref]$tokens,[ref]$errors)
    Assert ($errors.Count -eq 0) ('PowerShell parse error: '+$p.Name)
}
$Results.Add([ordered]@{test='windows_powershell_5_1_parse';passed=$true})
$g=Fixture 'install-repeat-rollback'
$before=@{};foreach($n in @('Resonance.exe','acsetup.cfg','Chinese.tra','player-save.sav')){$before[$n]=Hash (Join-Path $g $n)}
RunScript $Package '安装汉化.ps1' $g $true 'install-v1.1'
Assert ((Hash (Join-Path $g 'Chinese.tra')) -eq (Hash (Join-Path $Package 'PatchFiles\Chinese.tra'))) 'Installed TRA differs'
$backup=Join-Path $g '_Resonance_简中备份';$backupHash=Hash (Join-Path $backup 'backup_manifest.json')
RunScript $Package '安装汉化.ps1' $g $true 'repeat-v1.1'
Assert ((Hash (Join-Path $backup 'backup_manifest.json')) -eq $backupHash) 'Repeat overwrote first backup'
[IO.File]::AppendAllText((Join-Path $g 'acsetup.cfg'),"`r`n# player change")
[IO.File]::AppendAllText((Join-Path $g 'Chinese.tra'),'PLAYER CHANGE')
Remove-Item -LiteralPath (Join-Path $g 'agsfnt9.ttf')
RunScript $Package '回退汉化.ps1' $g $true 'rollback-modified-and-missing'
foreach($n in $before.Keys){Assert ((Hash (Join-Path $g $n)) -eq $before[$n]) ('Rollback mismatch: '+$n)}
Assert (-not(Test-Path -LiteralPath (Join-Path $g 'game28.dta'))) 'New payload left after rollback'
Assert (@(Get-ChildItem -LiteralPath $g -Directory -Filter '_Resonance_回退前备份_*').Count -eq 1) 'Changed-state preservation missing'
$Results.Add([ordered]@{test='rollback_restores_original_bytes_and_preserves_save_and_modified_state';passed=$true})
$g=Fixture 'old-version-upgrade'
RunScript $Old '安装汉化.ps1' $g $true 'install-v1.0.1'
$oldTra=Hash (Join-Path $g 'Chinese.tra')
RunScript $Package '安装汉化.ps1' $g $false 'reject-direct-old-upgrade'
Assert ((Hash (Join-Path $g 'Chinese.tra')) -eq $oldTra) 'Rejected upgrade changed old translation'
RunScript $Old '回退汉化.ps1' $g $true 'rollback-v1.0.1'
RunScript $Package '安装汉化.ps1' $g $true 'upgrade-after-old-rollback'
RunScript $Package '回退汉化.ps1' $g $true 'rollback-upgraded-v1.1'
$corrupt=Join-Path $WorkRoot 'corrupt-package';New-Item -ItemType Directory -Path $corrupt | Out-Null
Get-ChildItem -LiteralPath $Package -Force | Copy-Item -Destination $corrupt -Recurse
[IO.File]::AppendAllText((Join-Path $corrupt 'PatchFiles\Chinese.tra'),'CORRUPT')
$g=Fixture 'corruption-rejection';$exeHash=Hash (Join-Path $g 'Resonance.exe');$cfgHash=Hash (Join-Path $g 'acsetup.cfg')
RunScript $corrupt '安装汉化.ps1' $g $false 'reject-corrupt-payload'
Assert ((Hash (Join-Path $g 'Resonance.exe')) -eq $exeHash -and (Hash (Join-Path $g 'acsetup.cfg')) -eq $cfgHash) 'Corrupt install changed game'
Assert (-not(Test-Path -LiteralPath (Join-Path $g '_Resonance_简中备份'))) 'Corrupt install created backup'
$result=[ordered]@{version='1.1';fixture_only=$true;real_game_playtest=$false;note='Synthetic PE fixtures validate installer behavior only. No game binary was executed.';tests=@($Results.ToArray())}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path (Join-Path $Project 'qa') $ReportName) -Encoding UTF8
Write-Output ('Passed '+$Results.Count+' checks; fixture only.')
