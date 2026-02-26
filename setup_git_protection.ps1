# Setup Git Protection for Onboarding Code
# Run this once to set up your protected branch

Write-Host "🔒 Setting up Git protection for onboarding code..." -ForegroundColor Cyan

# Check current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Yellow

# Create backup of current work
$backupBranch = "backup/onboarding-working-$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
Write-Host "`n📦 Creating backup branch: $backupBranch" -ForegroundColor Green
git branch $backupBranch

# Create or switch to onboarding feature branch
Write-Host "`n🌿 Creating/switching to feature/onboarding-system branch..." -ForegroundColor Green
git checkout -b feature/onboarding-system 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Branch already exists, switching to it..." -ForegroundColor Yellow
    git checkout feature/onboarding-system
}

# Stage onboarding files
Write-Host "`n📝 Staging onboarding files..." -ForegroundColor Green
git add src/onboarding/
git add src/knowledge_graph/
git add src/lambda/lambda_whatsapp_kisaanmitra.py
git add src/lambda/deployment_package/
git add dashboard/streamlit_app.py
git add .gitattributes

# Commit
Write-Host "`n💾 Committing changes..." -ForegroundColor Green
git commit -m "feat: protected onboarding system with knowledge graph

- Farmer onboarding flow in Hindi
- Knowledge graph integration
- DynamoDB user profiles
- AI-powered information extraction
- Streamlit dashboard for visualization

Protected branch to prevent conflicts with other changes."

# Push to remote
Write-Host "`n🚀 Pushing to remote..." -ForegroundColor Green
git push -u origin feature/onboarding-system

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nYour onboarding code is now protected on: feature/onboarding-system" -ForegroundColor Cyan
Write-Host "Backup created at: $backupBranch" -ForegroundColor Cyan
Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Always work on feature/onboarding-system branch"
Write-Host "2. Deploy from this branch: cd src/lambda && ./deploy_updated_onboarding.ps1"
Write-Host "3. Your friend should work on their own branch"
Write-Host "4. Merge to main only when both are ready"
Write-Host "`nTo deploy: git checkout feature/onboarding-system && cd src/lambda && ./deploy_updated_onboarding.ps1"
