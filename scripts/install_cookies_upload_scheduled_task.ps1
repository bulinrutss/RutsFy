# Tarefa agendada: a cada 3 dias, exporta cookies e envia para a VPS RutsFy.
# Execute uma vez (PowerShell normal):
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force  # se ainda não tiver
#   & "E:\GitHub\sound\scripts\install_cookies_upload_scheduled_task.ps1"

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
$Script = Join-Path $PSScriptRoot "renew_and_upload_youtube_cookies.py"
$TaskName = "RutsFyUploadYouTubeCookies"

if (-not (Test-Path $Python)) {
    Write-Error "Python do venv não encontrado: $Python"
}
if (-not (Test-Path $Script)) {
    Write-Error "Script não encontrado: $Script"
}

$Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`"" -WorkingDirectory $Root
# 03:00 a cada 3 dias; Chrome costuma estar fechado (yt-dlp le o perfil).
$Trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 3 -At "03:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "RutsFy: renova youtube_cookies.txt e envia para Oracle a cada 3 dias"

Write-Host "[ok] Tarefa '$TaskName' criada - dispara a cada 3 dias as 03:00."
Write-Host "     Teste: $Python $Script"
Write-Host "     Log: C:\Users\svbul\Downloads\cokies\rutsfy-cookies-upload.log"
