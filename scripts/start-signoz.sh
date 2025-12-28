#!/bin/bash
# Start SigNoz observability stack for Sentinel
# This script launches SigNoz with all required services

set -e

echo "🚀 Starting SigNoz Observability Stack for Sentinel..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p docker/clickhouse/data
mkdir -p docker/clickhouse-metrics/data
mkdir -p docker/alertmanager/data
mkdir -p docker/data/signoz

# Start SigNoz stack
echo ""
echo "🐳 Starting Docker containers..."
docker compose -f docker-compose.observability.yml up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.observability.yml ps

echo ""
echo "✅ SigNoz is starting up!"
echo ""
echo "📍 Access Points:"
echo "   - SigNoz UI:        http://localhost:3301"
echo "   - OTLP gRPC:        localhost:4317"
echo "   - OTLP HTTP:        localhost:4318"
echo "   - Prometheus:       http://localhost:8889"
echo "   - Health Check:     http://localhost:13133"
echo ""
echo "🔍 View logs:"
echo "   docker compose -f docker-compose.observability.yml logs -f"
echo ""
echo "🛑 Stop SigNoz:"
echo "   docker compose -f docker-compose.observability.yml down"
echo ""
