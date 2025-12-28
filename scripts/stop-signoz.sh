#!/bin/bash
# Stop SigNoz observability stack

set -e

echo "🛑 Stopping SigNoz Observability Stack..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Stop all containers
docker compose -f docker-compose.observability.yml down

echo ""
echo "✅ SigNoz stopped successfully!"
echo ""
echo "💾 Data is preserved in ./docker directories"
echo ""
echo "🧹 To remove all data, run:"
echo "   docker compose -f docker-compose.observability.yml down -v"
echo "   rm -rf docker/clickhouse/data docker/clickhouse-metrics/data"
echo ""
