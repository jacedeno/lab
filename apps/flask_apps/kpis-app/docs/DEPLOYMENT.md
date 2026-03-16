# Deployment Guide — Flask KPI Dashboard

## Overview

The Flask KPI Dashboard runs as a Docker container managed via **Portainer** on the Docker host at `192.168.68.81`. The source code lives in the `jacedeno/lab` GitHub repository under `apps/flask_apps/kpis-app`.

## Prerequisites

- Docker host: `192.168.68.81` (hostname: `dockergeek`)
- Portainer CE: `https://192.168.68.81:9443`
- Git repo cloned on the server: `/root/apps/flask-kpis-app`
- Data directory (SQLite DB): `/root/apps/flask-kpis-app/data/kpi_data.db`

## Server Setup (one-time)

### 1. Clone the repository

```bash
ssh root@192.168.68.81
cd /root/apps
git clone git@github.com:jacedeno/lab.git
```

This gives you the full lab repo at `/root/apps/lab`. The app source is at:
```
/root/apps/lab/apps/flask_apps/kpis-app/
```

### 2. Configure Git (if not already done)

```bash
git config --global user.name "jacedeno"
git config --global user.email "jacedeno@geekendzone.com"
```

### 3. Ensure SSH key is set up for GitHub

```bash
# Check if key exists
cat ~/.ssh/id_ed25519.pub

# If not, generate one and add it to GitHub
ssh-keygen -t ed25519 -C "jacedeno@geekendzone.com"
cat ~/.ssh/id_ed25519.pub
# Copy the output and add it at: https://github.com/settings/keys
```

### 4. Ensure data directory exists

```bash
mkdir -p /root/apps/flask-kpis-app/data
# If migrating from old Streamlit app, copy the DB:
cp /root/lab/apps/streamlit_apps/kpis-app/data/kpi_data.db /root/apps/flask-kpis-app/data/
```

## Deployment Workflow

### Making changes (develop → build → deploy)

#### Step 1 — Pull latest code on the server

```bash
cd /root/apps/lab
git pull origin main
```

#### Step 2 — Rebuild the Docker image

```bash
cd /root/apps/lab/apps/flask_apps/kpis-app
docker build -t flask-kpi-dashboard .
```

#### Step 3 — Redeploy the stack

Option A — Via Portainer UI:
1. Go to **Stacks** → **flask-kpi-dashboard**
2. Click **Stop** then **Start** (or **Recreate** if you updated the compose)

Option B — Via CLI:
```bash
docker stop flask-kpi-dashboard
docker rm flask-kpi-dashboard
docker run -d \
  --name flask-kpi-dashboard \
  --restart unless-stopped \
  -p 8502:5000 \
  -v /root/apps/flask-kpis-app/data:/app/data \
  -e SECRET_KEY=f7k9x2m4p8q1w6v3j5n0b8t2y4r7e1a \
  -e RESEND_API_KEY=re_2rNouoD6_NNiTtmrULABvo1xGKCphB6EB \
  -e DATABASE_PATH=data/kpi_data.db \
  flask-kpi-dashboard
```

Option C — Quick redeploy (one-liner):
```bash
cd /root/apps/lab/apps/flask_apps/kpis-app && \
  git pull origin main && \
  docker build -t flask-kpi-dashboard . && \
  docker stop flask-kpi-dashboard && \
  docker rm flask-kpi-dashboard && \
  docker run -d \
    --name flask-kpi-dashboard \
    --restart unless-stopped \
    -p 8502:5000 \
    -v /root/apps/flask-kpis-app/data:/app/data \
    -e SECRET_KEY=f7k9x2m4p8q1w6v3j5n0b8t2y4r7e1a \
    -e RESEND_API_KEY=re_2rNouoD6_NNiTtmrULABvo1xGKCphB6EB \
    -e DATABASE_PATH=data/kpi_data.db \
    flask-kpi-dashboard
```

#### Step 4 — Verify

```bash
# Check container is running
docker ps | grep flask-kpi

# Check health
curl http://localhost:8502/health

# Check logs if something is wrong
docker logs flask-kpi-dashboard --tail 50
```

App URL: **http://192.168.68.81:8502**

## Portainer Stack Definition

If you need to recreate the stack in Portainer, use this compose:

```yaml
services:
  kpis-app:
    image: flask-kpi-dashboard
    container_name: flask-kpi-dashboard
    ports:
      - "8502:5000"
    volumes:
      - /root/apps/flask-kpis-app/data:/app/data
    restart: unless-stopped
    environment:
      - SECRET_KEY=f7k9x2m4p8q1w6v3j5n0b8t2y4r7e1a
      - RESEND_API_KEY=re_2rNouoD6_NNiTtmrULABvo1xGKCphB6EB
      - DATABASE_PATH=data/kpi_data.db
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:5000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

## Troubleshooting

| Issue | Command |
|-------|---------|
| Container won't start | `docker logs flask-kpi-dashboard` |
| DB permission error | `chmod 644 /root/apps/flask-kpis-app/data/kpi_data.db` |
| Port already in use | `docker ps -a` to find conflicting container |
| Health check failing | `curl -v http://localhost:8502/health` |
| Image not found | Rebuild: `docker build -t flask-kpi-dashboard .` |
