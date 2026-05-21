$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "H:\urbandatascience\envs\688y\python.exe"
$MainScript = Join-Path $ScriptDir "main.py"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Could not find the class Python environment at:"
    Write-Host $PythonExe
    Write-Host ""
    Write-Host "Try running this instead from PowerShell:"
    Write-Host "python main.py"
    exit 1
}

& $PythonExe $MainScript
