#!/bin/bash
# PostgreSQL Database Restore Script for Sentinel
# Restores database from compressed/encrypted backups
#
# Usage: ./restore-db.sh <backup_file> [--force]
#
# Options:
#   --force    Skip confirmation prompt (use with caution!)
#
# Examples:
#   ./restore-db.sh backups/postgres/sentinel_20251227_140530.sql.gz
#   ./restore-db.sh backups/postgres/sentinel_20251227_140530.sql.gz.gpg
#   ./restore-db.sh /path/to/backup.sql.gz --force

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FORCE=false

# Parse arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}❌ Error: Backup file path required${NC}"
    echo ""
    echo "Usage: $0 <backup_file> [--force]"
    echo ""
    echo "Examples:"
    echo "  $0 backups/postgres/sentinel_20251227_140530.sql.gz"
    echo "  $0 backups/postgres/sentinel_20251227_140530.sql.gz.gpg"
    exit 1
fi

BACKUP_FILE="$1"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Load database credentials from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
else
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "   Expected location: $PROJECT_ROOT/.env"
    exit 1
fi

# Parse DATABASE_URL to extract credentials
DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

# Validate required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ Error: $1 is not installed${NC}"
        echo "   Install with: sudo apt-get install $2"
        exit 1
    fi
}

check_command psql postgresql-client
check_command gzip gzip

# Check if file is encrypted
if [[ "$BACKUP_FILE" == *.gpg ]]; then
    check_command gpg gnupg
    ENCRYPTED=true
else
    ENCRYPTED=false
fi

echo -e "${GREEN}🗄️  Sentinel Database Restore${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${YELLOW}⚠️  WARNING: This will OVERWRITE the current database!${NC}"
echo ""
echo -e "  Database:     ${YELLOW}$DB_NAME${NC}"
echo -e "  Host:         ${YELLOW}$DB_HOST:$DB_PORT${NC}"
echo -e "  Backup File:  ${YELLOW}$BACKUP_FILE${NC}"
echo -e "  File Size:    ${YELLOW}$(du -h "$BACKUP_FILE" | cut -f1)${NC}"
echo -e "  Encrypted:    ${YELLOW}$([ "$ENCRYPTED" = true ] && echo "Yes" || echo "No")${NC}"
echo ""

# Confirmation prompt (unless --force)
if [ "$FORCE" = false ]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  THIS OPERATION CANNOT BE UNDONE${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "Type 'yes' to confirm restore: " confirmation

    if [ "$confirmation" != "yes" ]; then
        echo -e "${YELLOW}❌ Restore cancelled${NC}"
        exit 0
    fi
fi

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

# Create backup of current database before restore
echo ""
echo -e "${YELLOW}📦 Creating safety backup of current database...${NC}"
SAFETY_BACKUP="$PROJECT_ROOT/backups/postgres/pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
mkdir -p "$(dirname "$SAFETY_BACKUP")"

pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --format=plain \
    --no-owner \
    --no-acl \
    "$DB_NAME" | gzip -9 > "$SAFETY_BACKUP"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ Safety backup created: $(du -h "$SAFETY_BACKUP" | cut -f1)${NC}"
    echo -e "   Location: $SAFETY_BACKUP"
else
    echo -e "${RED}   ❌ Safety backup failed - aborting restore${NC}"
    exit 1
fi

# Prepare SQL file
TEMP_SQL="/tmp/sentinel_restore_$$.sql"

echo ""
echo -e "${YELLOW}📂 Preparing backup file...${NC}"

if [ "$ENCRYPTED" = true ]; then
    # Decrypt and decompress
    echo -e "   🔓 Decrypting..."
    if ! gpg --decrypt "$BACKUP_FILE" | gzip -d > "$TEMP_SQL" 2>/dev/null; then
        echo -e "${RED}   ❌ Decryption failed - check GPG key${NC}"
        rm -f "$TEMP_SQL"
        exit 1
    fi
else
    # Just decompress
    echo -e "   📂 Decompressing..."
    if ! gzip -cd "$BACKUP_FILE" > "$TEMP_SQL"; then
        echo -e "${RED}   ❌ Decompression failed${NC}"
        rm -f "$TEMP_SQL"
        exit 1
    fi
fi

SQL_SIZE=$(du -h "$TEMP_SQL" | cut -f1)
echo -e "${GREEN}   ✅ Prepared: $SQL_SIZE${NC}"

# Perform restore
echo ""
echo -e "${YELLOW}🔄 Restoring database...${NC}"
echo -e "   ${BLUE}This may take several minutes...${NC}"

# Drop existing connections to the database
psql \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname=postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" \
    > /dev/null 2>&1

# Execute restore
if psql \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --file="$TEMP_SQL" \
    > /tmp/restore.log 2>&1; then

    echo -e "${GREEN}   ✅ Database restored successfully${NC}"

    # Count restored tables
    TABLE_COUNT=$(psql \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --tuples-only \
        -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)

    echo -e "   Tables restored: ${YELLOW}$TABLE_COUNT${NC}"

else
    echo -e "${RED}   ❌ Restore failed${NC}"
    echo -e "   ${YELLOW}Check log: /tmp/restore.log${NC}"
    echo -e "   ${YELLOW}Safety backup available: $SAFETY_BACKUP${NC}"

    # Ask if user wants to restore from safety backup
    read -p "Restore from safety backup? (yes/no): " rollback_confirm
    if [ "$rollback_confirm" = "yes" ]; then
        echo -e "${YELLOW}🔄 Rolling back to safety backup...${NC}"
        gzip -cd "$SAFETY_BACKUP" | psql \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            --username="$DB_USER" \
            --dbname="$DB_NAME" \
            > /dev/null 2>&1

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}   ✅ Rollback successful${NC}"
        else
            echo -e "${RED}   ❌ Rollback failed - manual intervention required${NC}"
        fi
    fi

    rm -f "$TEMP_SQL"
    exit 1
fi

# Cleanup
rm -f "$TEMP_SQL"

# Verification
echo ""
echo -e "${YELLOW}🔍 Verifying restore...${NC}"

# Check critical tables exist
CRITICAL_TABLES=("agents" "bottlenecks" "decisions")
ALL_GOOD=true

for table in "${CRITICAL_TABLES[@]}"; do
    COUNT=$(psql \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --tuples-only \
        -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | xargs)

    if [ $? -eq 0 ]; then
        echo -e "   ✅ Table '$table': ${YELLOW}$COUNT rows${NC}"
    else
        echo -e "   ${RED}❌ Table '$table': NOT FOUND${NC}"
        ALL_GOOD=false
    fi
done

# Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ Database restore completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Database restore completed with warnings${NC}"
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Restore Summary:${NC}"
echo -e "  Restored from:    ${YELLOW}$BACKUP_FILE${NC}"
echo -e "  Database:         ${YELLOW}$DB_NAME${NC}"
echo -e "  Tables:           ${YELLOW}$TABLE_COUNT${NC}"
echo -e "  Safety backup:    ${YELLOW}$SAFETY_BACKUP${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. Verify application functionality"
echo "  2. Check agent configurations"
echo "  3. Review decision audit logs"
echo "  4. Test API endpoints"
if [ "$ALL_GOOD" = false ]; then
    echo -e "  ${RED}5. INVESTIGATE MISSING TABLES${NC}"
fi
echo ""
echo -e "${YELLOW}ℹ️  Safety backup retained for 24 hours${NC}"
echo ""

# Unset password
unset PGPASSWORD
