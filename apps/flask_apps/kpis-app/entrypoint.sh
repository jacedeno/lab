#!/bin/sh
set -e

# Ensure data directory exists and is writable
mkdir -p /app/data
chmod 755 /app/data

# Fix permissions on existing database if needed
if [ -f /app/data/kpi_data.db ]; then
    chmod 644 /app/data/kpi_data.db
fi

exec "$@"
