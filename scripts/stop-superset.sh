#!/bin/bash
# Stop Apache Superset analytics stack

set -e

echo "🛑 Stopping Apache Superset Analytics Stack..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Stop all containers
docker compose -f docker-compose.analytics.yml down

echo ""
echo "✅ Superset stopped successfully!"
echo ""
echo "💾 Data is preserved in Docker volumes"
echo ""
echo "🧹 To remove all data, run:"
echo "   docker compose -f docker-compose.analytics.yml down -v"
echo "   rm -rf superset/"
echo ""
