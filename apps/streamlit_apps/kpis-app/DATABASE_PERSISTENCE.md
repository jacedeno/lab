# Database Persistence Guide

## Overview

The Weekly KPI Dashboard now uses **SQLite database** for persistent data storage. This means your data will be saved and remain available even after:
- Restarting the application
- Stopping/starting Docker containers
- System reboots

## How It Works

### Database Location
- **Local Development**: `data/kpi_data.db`
- **Docker**: Stored in a Docker volume named `kpi-data`

### What Gets Stored
All week data including:
- Week number and date
- Personnel and working days
- All hours metrics (planned, executed)
- All KPI percentages
- Timestamps (created_at, updated_at)

## Database Features

### ✅ Automatic Initialization
- On first run, the database is created automatically
- Sample data (Weeks 39-41) is loaded if database is empty
- No manual setup required

### ✅ Data Validation
- Prevents duplicate week entries
- Validates data types
- Maintains data integrity

### ✅ Easy Management
- Add weeks through the UI
- Remove weeks through the UI
- All changes are immediately persisted

## Docker Persistence

### Volume Configuration

The `docker-compose.yml` file includes a named volume:

```yaml
volumes:
  kpi-data:/app/data
```

This ensures your database persists across container restarts.

### Testing Persistence

1. **Add some data:**
   ```bash
   docker-compose up -d
   # Open http://localhost:8501
   # Add a new week through the UI
   ```

2. **Restart the container:**
   ```bash
   docker-compose restart
   # Or
   docker-compose down
   docker-compose up -d
   ```

3. **Verify data is still there:**
   - Open http://localhost:8501
   - Your added week should still be visible

## Data Backup

### Backing Up Your Database

#### Docker Environment:

1. **Find the volume:**
   ```bash
   docker volume ls
   # Look for: weekly-kpi-rev_kpi-data or kpi-data
   ```

2. **Copy database file:**
   ```bash
   # Create backup directory
   mkdir -p backups
   
   # Copy from container
   docker cp weekly-kpi-dashboard:/app/data/kpi_data.db ./backups/kpi_data_$(date +%Y%m%d).db
   ```

#### Local Development:

```bash
# Simple copy
cp data/kpi_data.db backups/kpi_data_$(date +%Y%m%d).db
```

### Restoring from Backup

#### Docker Environment:

```bash
# Stop the container
docker-compose down

# Remove old volume (optional, creates backup first)
docker run --rm -v weekly-kpi-rev_kpi-data:/data -v $(pwd)/backups:/backup alpine cp /data/kpi_data.db /backup/kpi_data_old.db

# Copy backup to volume
docker run --rm -v weekly-kpi-rev_kpi-data:/data -v $(pwd)/backups:/backup alpine cp /backup/kpi_data_YYYYMMDD.db /data/kpi_data.db

# Start container
docker-compose up -d
```

#### Local Development:

```bash
cp backups/kpi_data_YYYYMMDD.db data/kpi_data.db
```

## Database Management

### Inspecting the Database

You can inspect the database using SQLite tools:

```bash
# Install sqlite3 if not already installed
# macOS
brew install sqlite3

# Ubuntu/Debian
sudo apt-get install sqlite3

# Access the database
sqlite3 data/kpi_data.db

# View tables
.tables

# View data
SELECT * FROM weeks_data;

# Exit
.quit
```

### Viewing Data in Docker Container

```bash
# Enter the container
docker exec -it weekly-kpi-dashboard /bin/sh

# Install sqlite3 (if not already)
apt-get update && apt-get install -y sqlite3

# Access database
sqlite3 /app/data/kpi_data.db

# Query data
SELECT week_name, week_date, plan_attainment FROM weeks_data ORDER BY week_num;

# Exit
.quit
exit
```

## Database Schema

The `weeks_data` table structure:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| week_name | TEXT | Week identifier (e.g., "Week 39") |
| week_num | INTEGER | Week number (1-52) |
| week_date | TEXT | Week date (MM/DD/YYYY) |
| personnel | INTEGER | Number of personnel |
| working_days | INTEGER | Working days in week |
| available_hours | INTEGER | Available work hours |
| planned_hrs_corrective | INTEGER | Planned corrective hours |
| planned_hrs_reliability | INTEGER | Planned reliability hours |
| executed_hrs_corrective | INTEGER | Executed corrective hours |
| executed_hrs_reliability | INTEGER | Executed reliability hours |
| planning_rate | INTEGER | Planning rate percentage |
| plan_attainment | INTEGER | Plan attainment percentage |
| plan_attainment_corrective | INTEGER | Corrective attainment % |
| plan_attainment_reliability | INTEGER | Reliability attainment % |
| unplanned_job_pct | INTEGER | Unplanned jobs percentage |
| pmr_pct | INTEGER | PMR percentage |
| pmr_completion | INTEGER | PMR completion percentage |
| unplanned_hrs_total | INTEGER | Total unplanned hours |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

## Troubleshooting

### Issue: Data Not Persisting in Docker

**Solution:**
1. Verify volume is configured:
   ```bash
   docker volume ls
   ```

2. Check volume mount:
   ```bash
   docker inspect weekly-kpi-dashboard | grep Mounts -A 20
   ```

3. Ensure volume is in docker-compose.yml:
   ```yaml
   volumes:
     - kpi-data:/app/data
   ```

### Issue: Database Locked Error

**Cause:** Multiple processes trying to access database

**Solution:**
1. Restart the container:
   ```bash
   docker-compose restart
   ```

2. If problem persists, rebuild:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Issue: Cannot Add Week (Duplicate Error)

**Cause:** Week number already exists

**Solution:**
- Check existing weeks in the dashboard
- Remove the duplicate week first, or
- Use a different week number

### Issue: Lost Data After Container Removal

**Cause:** Used `docker-compose down -v` which removes volumes

**Solution:**
- Never use `-v` flag unless you want to delete data
- Always use: `docker-compose down` (without -v)
- Restore from backup (see Backup section)

## Migration from Session State

If you were using the old version (session state storage), your data was not persistent. The new version automatically starts with sample data. You'll need to re-enter any custom data.

## Database Files Location

### Local Development:
```
weekly-kpi-rev/
├── data/
│   └── kpi_data.db       # SQLite database file
```

### Docker:
```
Docker Volume: kpi-data
Located at: /var/lib/docker/volumes/weekly-kpi-rev_kpi-data/_data/kpi_data.db
```

## Advanced Operations

### Exporting Data to CSV

```bash
sqlite3 data/kpi_data.db <<EOF
.headers on
.mode csv
.output weeks_export.csv
SELECT * FROM weeks_data ORDER BY week_num;
.quit
EOF
```

### Importing Data from CSV

Create a Python script:

```python
import sqlite3
import csv

conn = sqlite3.connect('data/kpi_data.db')
cursor = conn.cursor()

with open('weeks_import.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute('''
            INSERT INTO weeks_data (week_name, week_num, week_date, ...)
            VALUES (?, ?, ?, ...)
        ''', (row['week_name'], row['week_num'], ...))

conn.commit()
conn.close()
```

### Resetting Database

#### Docker:
```bash
docker-compose down
docker volume rm weekly-kpi-rev_kpi-data
docker-compose up -d
```

#### Local:
```bash
rm -rf data/kpi_data.db
# Restart the application - it will recreate with sample data
```

## Best Practices

1. **Regular Backups**: Schedule weekly backups of your database
2. **Test Restores**: Periodically test your backup restoration process
3. **Monitor Size**: Keep an eye on database file size (shouldn't grow too large with 52 weeks max)
4. **Use Docker Volumes**: For production, always use named volumes
5. **Don't Delete Volumes**: Avoid using `docker-compose down -v`

## Security Notes

- Database file contains business data - protect accordingly
- In production, consider encryption at rest
- Limit access to database file
- Regular security audits recommended

## Support

For issues related to database:
1. Check logs: `docker-compose logs -f kpi-dashboard`
2. Verify database file exists: `docker exec weekly-kpi-dashboard ls -la /app/data/`
3. Check permissions: Database directory should be writable

---

**Last Updated:** October 2025  
**Database Version:** SQLite 3  
**Application:** Weekly KPI Dashboard
