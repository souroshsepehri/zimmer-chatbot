#!/bin/bash

# Quick script to locate chatbot project
echo "Finding chatbot project..."
echo ""

# Search for app.py in backend directory
echo "Searching for backend/app.py..."
BACKEND_APP=$(find ~ -type f -name "app.py" -path "*/backend/app.py" 2>/dev/null | head -1)

if [ -n "$BACKEND_APP" ]; then
    echo "✅ Found: $BACKEND_APP"
    PROJECT_ROOT=$(dirname "$(dirname "$BACKEND_APP")")
    echo ""
    echo "Project root: $PROJECT_ROOT"
    echo ""
    echo "To navigate there, run:"
    echo "  cd $PROJECT_ROOT/backend"
    echo ""
    echo "Or to start from project root:"
    echo "  cd $PROJECT_ROOT"
else
    echo "❌ backend/app.py not found"
    echo ""
    echo "Searching for any app.py..."
    ANY_APP=$(find ~ -type f -name "app.py" 2>/dev/null | head -3)
    if [ -n "$ANY_APP" ]; then
        echo "Found app.py files:"
        echo "$ANY_APP"
    else
        echo "❌ No app.py found"
        echo ""
        echo "Your project might not be uploaded yet, or is in a different location."
        echo "Please check:"
        echo "  1. Did you upload/clone the project to the server?"
        echo "  2. Is it in a different directory?"
    fi
fi

echo ""
echo "Current directory: $(pwd)"
echo "Contents:"
ls -la



