#!/bin/bash

echo "=========================================="
echo "  Checking PM2 Errors"
echo "=========================================="
echo ""

echo "=== Backend Logs (last 20 lines) ==="
pm2 logs backend --lines 20 --nostream
echo ""

echo "=== Frontend Logs (last 20 lines) ==="
pm2 logs frontend --lines 20 --nostream
echo ""

echo "=== Backend Error Log ==="
pm2 logs backend --err --lines 20 --nostream
echo ""

echo "=== Frontend Error Log ==="
pm2 logs frontend --err --lines 20 --nostream
echo ""

echo "=== PM2 Process Info ==="
pm2 describe backend
echo ""
pm2 describe frontend

