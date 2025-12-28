#!/bin/bash
# Start Apache Superset analytics stack for Sentinel
# This script launches Superset with all required services

set -e

echo "🚀 Starting Apache Superset Analytics Stack for Sentinel..."
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
mkdir -p superset
mkdir -p docker/redis/data

# Check if Sentinel PostgreSQL is running
echo ""
echo "🔍 Checking for Sentinel PostgreSQL..."
if ! docker network inspect sentinel_default > /dev/null 2>&1; then
    echo "⚠️  Warning: Sentinel PostgreSQL network not found."
    echo "   Superset will not be able to connect to Sentinel database."
    echo "   Make sure Sentinel is running before querying data."
fi

# Start Superset stack
echo ""
echo "🐳 Starting Docker containers..."
docker compose -f docker-compose.analytics.yml up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.analytics.yml ps

echo ""
echo "✅ Superset is starting up!"
echo ""
echo "📍 Access Points:"
echo "   - Superset UI:      http://localhost:8088"
echo "   - Default Login:    admin / admin"
echo "   - Redis:            localhost:6379"
echo ""
echo "🔗 Sentinel Database Connection (Add in Superset UI):"
echo "   Host: host.docker.internal"
echo "   Port: 5432"
echo "   Database: sentinel"
echo "   User: sentinel"
echo "   Password: [your password]"
echo "   Connection String: postgresql://sentinel:password@host.docker.internal:5432/sentinel"
echo ""
echo "📚 Next Steps:"
echo "   1. Log in to Superset at http://localhost:8088"
echo "   2. Add Sentinel PostgreSQL as a database connection"
echo "   3. Use SQL queries from superset/dashboard_queries.sql"
echo "   4. Create dashboards for your business metrics"
echo ""
echo "🔍 View logs:"
echo "   docker compose -f docker-compose.analytics.yml logs -f"
echo ""
echo "🛑 Stop Superset:"
echo "   docker compose -f docker-compose.analytics.yml down"
echo ""
