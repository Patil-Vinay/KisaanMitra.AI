# Clear all user data from DynamoDB tables

Write-Host "=== Clearing All User Data ===" -ForegroundColor Cyan

# Get all users from conversations
Write-Host "`nFetching users from conversations..." -ForegroundColor Yellow
$convResult = aws dynamodb scan --table-name kisaanmitra-conversations --projection-expression user_id --output json
$conversations = $convResult | ConvertFrom-Json
$uniqueUsers = $conversations.Items | ForEach-Object { $_.user_id.S } | Sort-Object -Unique

Write-Host "Found $($uniqueUsers.Count) unique users: $($uniqueUsers -join ', ')" -ForegroundColor Cyan

# Delete from all tables
foreach ($userId in $uniqueUsers) {
    Write-Host "`nDeleting user: $userId" -ForegroundColor Yellow
    
    # Delete from user-profiles
    Write-Host "  - Deleting from user-profiles..." -ForegroundColor Gray
    aws dynamodb delete-item --table-name kisaanmitra-user-profiles --key ('{"user_id":{"S":"' + $userId + '"}}') 2>$null
    
    # Delete from onboarding
    Write-Host "  - Deleting from onboarding..." -ForegroundColor Gray
    aws dynamodb delete-item --table-name kisaanmitra-onboarding --key ('{"user_id":{"S":"' + $userId + '"}}') 2>$null
    
    # Delete all conversations for this user
    Write-Host "  - Deleting conversations..." -ForegroundColor Gray
    $userConvs = aws dynamodb query --table-name kisaanmitra-conversations --key-condition-expression "user_id = :uid" --expression-attribute-values ('{":uid":{"S":"' + $userId + '"}}') --output json | ConvertFrom-Json
    
    foreach ($conv in $userConvs.Items) {
        $timestamp = $conv.timestamp.S
        aws dynamodb delete-item --table-name kisaanmitra-conversations --key ('{"user_id":{"S":"' + $userId + '"},"timestamp":{"S":"' + $timestamp + '"}}') 2>$null
    }
}

Write-Host "`n=== Verification ===" -ForegroundColor Cyan
Write-Host "User Profiles:" -ForegroundColor Yellow
aws dynamodb scan --table-name kisaanmitra-user-profiles --select COUNT

Write-Host "`nOnboarding States:" -ForegroundColor Yellow
aws dynamodb scan --table-name kisaanmitra-onboarding --select COUNT

Write-Host "`nConversations:" -ForegroundColor Yellow
aws dynamodb scan --table-name kisaanmitra-conversations --select COUNT

Write-Host "`n✅ All user data cleared!" -ForegroundColor Green
