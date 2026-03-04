# Daily Price Forecasting Training - Windows Task Scheduler Setup
# Runs every morning at 6:00 AM IST

$TaskName = "KisaanMitra-DailyPriceTraining"
$ScriptPath = "$PSScriptRoot\..\src\price_forecasting\daily_trainer.py"
$PythonPath = "python"  # Adjust if needed
$LogPath = "$PSScriptRoot\..\logs\daily_training.log"

Write-Host "=" -NoNewline; Write-Host ("=" * 59)
Write-Host "KISAANMITRA - DAILY PRICE TRAINING SETUP"
Write-Host "=" -NoNewline; Write-Host ("=" * 59)

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "`n⚠️  Task '$TaskName' already exists."
    $Response = Read-Host "Do you want to remove and recreate it? (y/n)"
    
    if ($Response -eq 'y' -or $Response -eq 'Y') {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Removed existing task"
    } else {
        Write-Host "❌ Setup cancelled"
        exit 1
    }
}

# Create action - run Python script
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "$ScriptPath" `
    -WorkingDirectory "$PSScriptRoot\.."

# Create trigger - daily at 6:00 AM
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00AM"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily price forecasting training for KisaanMitra - Fetches AgMarkNet data, trains Prophet models, uploads to DynamoDB" `
    -User $env:USERNAME

Write-Host "`n✅ Task created successfully!"
Write-Host "`n📋 TASK DETAILS:"
Write-Host "   Name: $TaskName"
Write-Host "   Schedule: Daily at 6:00 AM"
Write-Host "   Script: $ScriptPath"
Write-Host "   Log: $LogPath"

Write-Host "`n🔧 MANUAL COMMANDS:"
Write-Host "   Run now:    schtasks /Run /TN `"$TaskName`""
Write-Host "   View task:  Get-ScheduledTask -TaskName `"$TaskName`""
Write-Host "   Delete:     Unregister-ScheduledTask -TaskName `"$TaskName`" -Confirm:`$false"

Write-Host "`n💡 TEST THE SCRIPT NOW:"
Write-Host "   python $ScriptPath"

Write-Host "`n" + ("=" * 60)
