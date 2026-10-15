#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore_database.sh <path_to_backup.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
echo "Restoring database from $BACKUP_FILE..."

if [ -n "$DATABASE_URL" ]; then
    gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"
else
    gunzip -c "$BACKUP_FILE" | psql -U postgres -h localhost -d msme
fi

echo "Database restore completed successfully."
