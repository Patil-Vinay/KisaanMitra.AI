#!/bin/bash

# Create archive directory
mkdir -p docs/archive

# Essential docs to keep in root
ESSENTIAL=(
    "README.md"
    "ARCHITECTURE.md"
    "AWS_AI_SUBMISSION_GUIDE.md"
    "AWS_ARCHITECTURE_VISUAL.md"
    "SUBMISSION_PACKAGE.md"
    "FEATURES_LIST.md"
    "SAMPLE_COMMANDS.md"
    "QUICK_REFERENCE.md"
    "DISEASE_ALERT_SYSTEM.md"
    "HYPERLOCAL_ALERT_DEMO.md"
    "SUBMISSION_READY.md"
)

# Move all MD files except essential ones to archive
for file in *.md; do
    if [[ -f "$file" ]]; then
        # Check if file is in essential list
        is_essential=false
        for essential in "${ESSENTIAL[@]}"; do
            if [[ "$file" == "$essential" ]]; then
                is_essential=true
                break
            fi
        done
        
        # Move to archive if not essential
        if [[ "$is_essential" == false ]]; then
            echo "Archiving: $file"
            git mv "$file" "docs/archive/" 2>/dev/null || mv "$file" "docs/archive/"
        else
            echo "Keeping: $file"
        fi
    fi
done

echo ""
echo "Cleanup complete!"
echo "Essential docs kept in root: ${#ESSENTIAL[@]}"
echo "Archived docs moved to docs/archive/"
