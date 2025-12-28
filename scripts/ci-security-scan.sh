#!/bin/bash
set -e

# Sentinel CI Security Scan Script
# Usage: ./scripts/ci-security-scan.sh [API_URL]

API_URL="${1:-http://localhost:8000}"

echo "🔒 Starting Security Scan..."

# 1. Generate SARIF Report (ESLint)
echo "   Running ESLint..."
cd web
npm run lint:sarif
cd ..

# 2. Trigger Sentinel Ingestion
echo "   Triggering Sentinel Aggregation at $API_URL..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/orchestrate")

if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ Sentinel Scan Complete. Vulnerabilities ingested."
    exit 0
else
    echo "❌ Sentinel Ingestion Failed (HTTP $RESPONSE)."
    exit 1
fi
