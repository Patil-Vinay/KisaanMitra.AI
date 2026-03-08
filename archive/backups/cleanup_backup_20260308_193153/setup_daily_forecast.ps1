# Setup Daily Price Forecast Update
# Creates a Windows Task Scheduler task to run every morning at 6 AM

$TaskName = "KisaanMitra-DailyPriceForecast"
$ScriptPath = "$PSScriptRoot\..\src\price_forecasting\daily_update.py"
$PythonPath = (Get-Command python).Source
$WorkingDir = "$PSScriptRoot\.."

Write-Host "Setting up daily price forecast update..." -ForegroundColor Cyan

# Create task action
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $WorkingDir

# Create trigger (daily at 6 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

# Create task settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Daily price forecast update for KisaanMitra" -Force
    Write-Host "Task scheduled successfully!" -ForegroundColor Green
    Write-Host "   Task Name: $TaskName" -ForegroundColor Yellow
    Write-Host "   Schedule: Daily at 6:00 AM" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To view the task:" -ForegroundColor Cyan
    Write-Host "   Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "To run manually:" -ForegroundColor Cyan
    Write-Host "   Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
} catch {
    Write-Host "Error creating scheduled task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to run this script as Administrator" -ForegroundColor Yellow
}
