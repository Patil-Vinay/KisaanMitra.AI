# Git Collaboration Guide - Protecting Onboarding Code

## Problem
Your friend is pushing changes to GitHub that could overwrite the working onboarding logic.

## Solution: Branch-Based Workflow

### 1. Create a Protected Branch for Onboarding

```powershell
# Create and switch to onboarding branch
git checkout -b feature/onboarding-system

# Push your onboarding work to this branch
git add src/onboarding/ src/knowledge_graph/ src/lambda/lambda_whatsapp_kisaanmitra.py
git commit -m "feat: working onboarding system with knowledge graph"
git push origin feature/onboarding-system
```

### 2. Your Friend Works on a Separate Branch

Your friend should work on their own branch:

```powershell
# Friend creates their own branch
git checkout -b feature/friend-changes
git push origin feature/friend-changes
```

### 3. Protected Files Strategy

Create a `.gitattributes` file to mark critical files:

```
# Critical onboarding files - require careful merge
src/onboarding/** merge=ours
src/knowledge_graph/** merge=ours
src/lambda/lambda_whatsapp_kisaanmitra.py merge=ours
```

### 4. Daily Workflow

**Your Workflow:**
```powershell
# Always work on your branch
git checkout feature/onboarding-system

# Pull latest changes from main (if needed)
git fetch origin main
git merge origin/main --no-commit

# If conflicts, keep your onboarding code
git checkout --ours src/onboarding/
git checkout --ours src/knowledge_graph/
git checkout --ours src/lambda/lambda_whatsapp_kisaanmitra.py

# Commit and push
git commit -m "merge: integrated main changes, kept onboarding logic"
git push origin feature/onboarding-system
```

**Friend's Workflow:**
```powershell
# Friend works on their branch
git checkout feature/friend-changes
# ... make changes ...
git push origin feature/friend-changes
```

### 5. Deployment Strategy

**Option A: Deploy from Your Branch (Recommended)**
```powershell
# Deploy directly from your onboarding branch
git checkout feature/onboarding-system
cd src/lambda
./deploy_updated_onboarding.ps1
```

**Option B: Selective Merge to Main**
```powershell
# Merge only onboarding files to main
git checkout main
git checkout feature/onboarding-system -- src/onboarding/
git checkout feature/onboarding-system -- src/knowledge_graph/
git checkout feature/onboarding-system -- src/lambda/lambda_whatsapp_kisaanmitra.py
git commit -m "merge: onboarding system from feature branch"
git push origin main
```

### 6. Critical Files to Protect

These files contain your working onboarding logic:

1. `src/onboarding/farmer_onboarding.py` - Onboarding state machine
2. `src/knowledge_graph/village_graph.py` - Knowledge graph manager
3. `src/lambda/lambda_whatsapp_kisaanmitra.py` - Main Lambda handler with onboarding checks
4. `src/lambda/deployment_package/` - Deployment files

### 7. Communication Protocol

**Before Merging:**
1. Check what files your friend changed: `git diff origin/main feature/friend-changes`
2. If they touched onboarding files, review carefully
3. Test locally before deploying

**Conflict Resolution:**
- If friend's changes don't touch onboarding → Safe to merge
- If friend's changes touch Lambda handler → Manual review required
- If friend's changes touch onboarding modules → Keep your version

### 8. Quick Commands

**Check current branch:**
```powershell
git branch
```

**See what changed in friend's commits:**
```powershell
git fetch origin
git log origin/main..HEAD --oneline
git diff origin/main
```

**Backup your working code:**
```powershell
# Create backup branch
git checkout -b backup/onboarding-working-$(Get-Date -Format "yyyy-MM-dd")
git push origin backup/onboarding-working-$(Get-Date -Format "yyyy-MM-dd")
```

**Restore from backup if needed:**
```powershell
git checkout backup/onboarding-working-2026-02-27
git checkout -b feature/onboarding-system-restored
```

### 9. GitHub Branch Protection (Optional)

If you have admin access to the repo, protect the onboarding branch:

1. Go to GitHub → Settings → Branches
2. Add rule for `feature/onboarding-system`
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Lock branch (prevent force push)

### 10. Alternative: Separate Repository

If conflicts persist, consider:

```powershell
# Create separate repo for onboarding
mkdir kisaanmitra-onboarding
cd kisaanmitra-onboarding
git init
git remote add origin https://github.com/your-username/kisaanmitra-onboarding.git

# Copy onboarding files
cp -r ../kisaanmitra/src/onboarding .
cp -r ../kisaanmitra/src/knowledge_graph .
cp ../kisaanmitra/src/lambda/lambda_whatsapp_kisaanmitra.py .

git add .
git commit -m "initial: onboarding system"
git push -u origin main
```

## Recommended Approach

**Best Solution:** Use separate branches + deploy from your branch

1. You work on `feature/onboarding-system`
2. Friend works on `feature/friend-changes`
3. You deploy directly from your branch
4. Merge to main only when both are ready
5. Always keep a backup branch

This way:
- Your onboarding code stays protected
- Friend can work independently
- No conflicts during development
- Clean deployment process
