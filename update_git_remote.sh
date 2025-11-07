#!/bin/bash

# Update Git Remote Repository Script
echo "========================================"
echo "   Updating Git Remote Repository"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"
echo ""

echo "Current Git Remotes:"
git remote -v
echo ""

echo "Removing all existing remotes..."
git remote remove origin 2>/dev/null
git remote remove upstream 2>/dev/null
git remote remove backup 2>/dev/null

echo ""
echo "Adding new remote: https://github.com/souroshsepehri/zimmer-chatbot.git"
git remote add origin https://github.com/souroshsepehri/zimmer-chatbot.git

echo ""
echo "Updated Git Remotes:"
git remote -v
echo ""

echo "========================================"
echo "   Git Remote Updated Successfully!"
echo "========================================"
echo ""
echo "To verify connection:"
echo "  git remote show origin"
echo ""
echo "To fetch from new remote:"
echo "  git fetch origin"
echo ""
