# Simple script to clear DynamoDB tables

Write-Host "Clearing kisaanmitra-user-profiles..." -ForegroundColor Cyan
aws dynamodb delete-item --table-name kisaanmitra-user-profiles --key '{\"user_id\":{\"S\":\"919000000003\"}}' --region ap-south-1
aws dynamodb delete-item --table-name kisaanmitra-user-profiles --key '{\"user_id\":{\"S\":\"919000000002\"}}' --region ap-south-1

Write-Host "Clearing kisaanmitra-onboarding..." -ForegroundColor Cyan
aws dynamodb delete-item --table-name kisaanmitra-onboarding --key '{\"user_id\":{\"S\":\"919000000003\"}}' --region ap-south-1
aws dynamodb delete-item --table-name kisaanmitra-onboarding --key '{\"user_id\":{\"S\":\"919000000002\"}}' --region ap-south-1

Write-Host "Clearing kisaanmitra-conversations..." -ForegroundColor Cyan
$conversations = aws dynamodb scan --table-name kisaanmitra-conversations --region ap-south-1 | ConvertFrom-Json
foreach ($item in $conversations.Items) {
    $userId = $item.user_id.S
    $timestamp = $item.timestamp.S
    aws dynamodb delete-item --table-name kisaanmitra-conversations --key ('{\"user_id\":{\"S\":\"' + $userId + '\"},\"timestamp\":{\"S\":\"' + $timestamp + '\"}}') --region ap-south-1
}

Write-Host ""
Write-Host "Verification:" -ForegroundColor Yellow
aws dynamodb scan --table-name kisaanmitra-user-profiles --region ap-south-1 --select COUNT
aws dynamodb scan --table-name kisaanmitra-onboarding --region ap-south-1 --select COUNT
aws dynamodb scan --table-name kisaanmitra-conversations --region ap-south-1 --select COUNT

Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green
