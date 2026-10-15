#!/usr/bin/env bash
set -e

BACKUP_DIR="${BACKUP_DIR:-/var/backups/msme}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/msme_backup_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "Starting PostgreSQL database backup at $TIMESTAMP..."
if [ -n "$DATABASE_URL" ]; then
    pg_dump "$DATABASE_URL" | gzip > "$FILENAME"
else
    pg_dump -U postgres -h localhost -d msme | gzip > "$FILENAME"
fi

echo "Backup completed successfully: $FILENAME"
