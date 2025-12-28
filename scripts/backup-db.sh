#!/bin/bash
# PostgreSQL Database Backup Script for Sentinel
# Creates compressed, timestamped backups with optional encryption
#
# Usage: ./backup-db.sh [--encrypt] [--retention-days 30]
#
# Options:
#   --encrypt          Encrypt backup with GPG (requires GPG key configured)
#   --retention-days N Delete backups older than N days (default: 30)
#
# Examples:
#   ./backup-db.sh                          # Basic backup
#   ./backup-db.sh --encrypt                # Encrypted backup
#   ./backup-db.sh --retention-days 7       # Keep only 7 days of backups

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
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups/postgres}"
RETENTION_DAYS=30
ENCRYPT=false
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Load database credentials from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
else
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "   Expected location: $PROJECT_ROOT/.env"
    exit 1
fi

# Parse DATABASE_URL to extract credentials
# Format: postgresql://user:password@host:port/database
DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --encrypt)
            ENCRYPT=true
            shift
            ;;
        --retention-days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--encrypt] [--retention-days N]"
            echo ""
            echo "Options:"
            echo "  --encrypt          Encrypt backup with GPG"
            echo "  --retention-days N Delete backups older than N days (default: 30)"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Validate required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ Error: $1 is not installed${NC}"
        echo "   Install with: sudo apt-get install $2"
        exit 1
    fi
}

check_command pg_dump postgresql-client
check_command gzip gzip

if [ "$ENCRYPT" = true ]; then
    check_command gpg gnupg
fi

echo -e "${GREEN}🗄️  Sentinel Database Backup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Database:     ${YELLOW}$DB_NAME${NC}"
echo -e "  Host:         ${YELLOW}$DB_HOST:$DB_PORT${NC}"
echo -e "  Timestamp:    ${YELLOW}$TIMESTAMP${NC}"
echo -e "  Backup Dir:   ${YELLOW}$BACKUP_DIR${NC}"
echo -e "  Encryption:   ${YELLOW}$([ "$ENCRYPT" = true ] && echo "Enabled" || echo "Disabled")${NC}"
echo -e "  Retention:    ${YELLOW}$RETENTION_DAYS days${NC}"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup filename
BACKUP_FILE="$BACKUP_DIR/sentinel_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"
FINAL_FILE="$COMPRESSED_FILE"

if [ "$ENCRYPT" = true ]; then
    FINAL_FILE="${COMPRESSED_FILE}.gpg"
fi

# Export password for pg_dump
export PGPASSWORD="$DB_PASSWORD"

# Perform backup
echo -e "${YELLOW}📦 Creating database dump...${NC}"

pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --format=plain \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}   ✅ Dump created: $BACKUP_SIZE${NC}"
else
    echo -e "${RED}   ❌ Dump failed${NC}"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Compress backup
echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
gzip -9 "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    COMPRESSION_RATIO=$(echo "scale=1; $(stat -f%z "$COMPRESSED_FILE") * 100 / $(stat -f%z "$BACKUP_FILE" 2>/dev/null || echo "1")" | bc 2>/dev/null || echo "N/A")
    echo -e "${GREEN}   ✅ Compressed: $COMPRESSED_SIZE (${COMPRESSION_RATIO}% of original)${NC}"
else
    echo -e "${RED}   ❌ Compression failed${NC}"
    exit 1
fi

# Encrypt if requested
if [ "$ENCRYPT" = true ]; then
    echo -e "${YELLOW}🔐 Encrypting backup...${NC}"

    # Check for GPG key
    GPG_RECIPIENT="${GPG_RECIPIENT:-admin@sentinel.local}"

    if ! gpg --list-keys "$GPG_RECIPIENT" &> /dev/null; then
        echo -e "${RED}   ❌ GPG key not found for: $GPG_RECIPIENT${NC}"
        echo "   Set GPG_RECIPIENT environment variable or generate a GPG key:"
        echo "   gpg --gen-key"
        exit 1
    fi

    gpg --encrypt --recipient "$GPG_RECIPIENT" --trust-model always "$COMPRESSED_FILE"

    if [ $? -eq 0 ]; then
        ENCRYPTED_SIZE=$(du -h "$FINAL_FILE" | cut -f1)
        echo -e "${GREEN}   ✅ Encrypted: $ENCRYPTED_SIZE${NC}"
        rm "$COMPRESSED_FILE"  # Remove unencrypted version
    else
        echo -e "${RED}   ❌ Encryption failed${NC}"
        exit 1
    fi
fi

# Verify backup integrity
echo -e "${YELLOW}🔍 Verifying backup integrity...${NC}"

if [ "$ENCRYPT" = true ]; then
    # For encrypted files, just check if GPG can read header
    if gpg --list-packets "$FINAL_FILE" &> /dev/null; then
        echo -e "${GREEN}   ✅ Backup is valid and encrypted${NC}"
    else
        echo -e "${RED}   ❌ Backup verification failed${NC}"
        exit 1
    fi
else
    # For compressed files, test gzip integrity
    if gzip -t "$FINAL_FILE" 2>/dev/null; then
        echo -e "${GREEN}   ✅ Backup is valid${NC}"
    else
        echo -e "${RED}   ❌ Backup verification failed${NC}"
        exit 1
    fi
fi

# Cleanup old backups
echo -e "${YELLOW}🧹 Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"

DELETED_COUNT=0
while IFS= read -r old_backup; do
    if [ -n "$old_backup" ]; then
        rm -f "$old_backup"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    fi
done < <(find "$BACKUP_DIR" -name "sentinel_*.sql.gz*" -mtime +$RETENTION_DAYS)

if [ $DELETED_COUNT -gt 0 ]; then
    echo -e "${GREEN}   ✅ Deleted $DELETED_COUNT old backup(s)${NC}"
else
    echo -e "   ℹ️  No old backups to delete${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Backup completed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Backup File:  ${YELLOW}$FINAL_FILE${NC}"
echo -e "  Size:         ${YELLOW}$(du -h "$FINAL_FILE" | cut -f1)${NC}"
echo -e "  Database:     ${YELLOW}$DB_NAME${NC}"
echo -e "  Tables:       ${YELLOW}$(gzip -cd "$COMPRESSED_FILE" 2>/dev/null | grep -c "CREATE TABLE" || echo "encrypted")${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  - Store backup in secure off-site location"
echo "  - Test restore procedure: ./restore-db.sh $FINAL_FILE"
if [ "$ENCRYPT" = false ]; then
    echo "  - Consider encrypting backups: ./backup-db.sh --encrypt"
fi
echo "  - Schedule regular backups via cron:"
echo "    0 2 * * * cd $PROJECT_ROOT && ./scripts/backup-db.sh"
echo ""

# Unset password
unset PGPASSWORD
