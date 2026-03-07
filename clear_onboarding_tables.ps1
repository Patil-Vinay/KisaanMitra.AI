# Clear Onboarding DynamoDB Tables

Write-Host "=================================================="
Write-Host "Clearing Onboarding DynamoDB Tables"
Write-Host "=================================================="
Write-Host ""

$region = "ap-south-1"
$tables = @(
    "kisaanmitra-user-profiles",
    "kisaanmitra-onboarding",
    "kisaanmitra-conversations"
)

foreach ($tableName in $tables) {
    Write-Host "Clearing $tableName..." -ForegroundColor Cyan
    
    # Get all items
    $scanResult = aws dynamodb scan --table-name $tableName --region $region | ConvertFrom-Json
    $items = $scanResult.Items
    
    if ($items.Count -eq 0) {
        Write-Host "  ✓ $tableName is already empty" -ForegroundColor Green
        continue
    }
    
    Write-Host "  Found $($items.Count) items" -ForegroundColor Yellow
    
    # Get table key schema
    $tableInfo = aws dynamodb describe-table --table-name $tableName --region $region | ConvertFrom-Json
    $keySchema = $tableInfo.Table.KeySchema
    
    # Extract key names
    $hashKey = ($keySchema | Where-Object { $_.KeyType -eq "HASH" }).AttributeName
    $rangeKey = ($keySchema | Where-Object { $_.KeyType -eq "RANGE" }).AttributeName
    
    # Delete each item
    $deleted = 0
    foreach ($item in $items) {
        # Build delete request
        $key = @{}
        $key[$hashKey] = $item.$hashKey
        
        if ($rangeKey) {
            $key[$rangeKey] = $item.$rangeKey
        }
        
        $keyJson = $key | ConvertTo-Json -Compress
        
        # Delete item
        aws dynamodb delete-item --table-name $tableName --key $keyJson --region $region | Out-Null
        $deleted++
    }
    
    Write-Host "  ✓ Deleted $deleted items from $tableName" -ForegroundColor Green
}

Write-Host ""
Write-Host "=================================================="
Write-Host "Verification"
Write-Host "=================================================="

foreach ($tableName in $tables) {
    $countResult = aws dynamodb scan --table-name $tableName --region $region --select COUNT | ConvertFrom-Json
    $count = $countResult.Count
    $color = if ($count -eq 0) { "Green" } else { "Yellow" }
    Write-Host "${tableName}: $count items" -ForegroundColor $color
}

Write-Host ""
Write-Host "✅ All onboarding tables cleared!" -ForegroundColor Green
