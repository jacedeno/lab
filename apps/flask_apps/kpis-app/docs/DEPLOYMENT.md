# Deployment Guide — Flask KPI Dashboard

## Overview

The Flask KPI Dashboard runs as a Docker container managed via **Portainer** on the
Docker host at `192.168.68.81` (hostname: `dockergeek`). The source code lives in the
[jacedeno/lab](https://github.com/jacedeno/lab) GitHub repository under
`apps/flask_apps/kpis-app`.

| Resource | Location |
|----------|----------|
| Portainer UI | https://192.168.68.81:9443 |
| App (internal) | http://192.168.68.81:8502 |
| App (public) | https://kpis.cedeno.app (via Cloudflare Tunnel) |
| Git repo on server | `/root/lab` |
| App source on server | `/root/lab/apps/flask_apps/kpis-app` |
| SQLite database | `/root/apps/flask-kpis-app/data/kpi_data.db` |

## Server Setup (one-time, already done)

### 1. Git repository

The repo is cloned at `/root/lab` using HTTPS:

```bash
cd /root && git clone https://github.com/jacedeno/lab.git
```

### 2. Data directory

The SQLite database lives **outside** the repo so it persists across container rebuilds:

```bash
# Create the data directory
mkdir -p /root/apps/flask-kpis-app/data

# Ensure correct permissions (directory must be writable for SQLite journal files)
chmod 777 /root/apps/flask-kpis-app/data
chmod 666 /root/apps/flask-kpis-app/data/kpi_data.db
```

### 3. Portainer stack

The stack `flask-kpi-dashboard` is configured in Portainer with the compose definition
shown in the [Portainer Stack Definition](#portainer-stack-definition) section below.

---

## How to Modify and Redeploy

Follow these steps whenever you make changes to the application code.

### Step 1 — Edit and commit changes

You can edit code either on the server directly or from a development machine.

**From the server:**

```bash
# Navigate to the app directory
cd /root/lab/apps/flask_apps/kpis-app

# Make your changes, then commit and push
git add -A
git commit -m "Description of changes"
git push origin main
```

**From a development machine:**

```bash
# Make changes locally, commit and push
cd ~/repos/lab
git add apps/flask_apps/kpis-app/
git commit -m "Description of changes"
git push origin main
```

Then pull on the server:

```bash
# Fetch the latest code on the server
cd /root/lab && git pull origin main
```

### Step 2 — Rebuild the Docker image

```bash
# Build a new image from the updated source code
cd /root/lab/apps/flask_apps/kpis-app && docker build -t flask-kpi-dashboard .
```

### Step 3 — Redeploy via Portainer

1. Open **Portainer** at https://192.168.68.81:9443
2. Go to **Stacks** > **flask-kpi-dashboard**
3. Click **Stop this stack**
4. Click **Start this stack**

The stack references the local `flask-kpi-dashboard` image, so it will pick up
the newly built image automatically.

### Step 4 — Verify

```bash
# Confirm the container is running and healthy
docker ps | grep flask-kpi

# Test the health endpoint
curl http://localhost:8502/health

# Check application logs if something looks wrong
docker logs flask-kpi-dashboard --tail 50
```

Then open https://kpis.cedeno.app/ in the browser to confirm.

---

## Quick Redeploy (single command)

For convenience, pull + build + redeploy in one shot from the server:

```bash
cd /root/lab && git pull origin main && cd apps/flask_apps/kpis-app && docker build -t flask-kpi-dashboard . && docker stop flask-kpi-dashboard && docker rm flask-kpi-dashboard && docker run -d --name flask-kpi-dashboard --restart unless-stopped -p 8502:5000 -v /root/apps/flask-kpis-app/data:/app/data -e SECRET_KEY=f7k9x2m4p8q1w6v3j5n0b8t2y4r7e1a -e RESEND_API_KEY=re_2rNouoD6_NNiTtmrULABvo1xGKCphB6EB -e DATABASE_PATH=data/kpi_data.db flask-kpi-dashboard
```

> **Note:** After using this CLI method, the container will no longer be managed by the
> Portainer stack. To return to Portainer management, redeploy the stack from the
> Portainer UI instead (Step 3 above).

---

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

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `docker logs flask-kpi-dashboard` |
| `readonly database` error | Fix permissions: `chmod 777 /root/apps/flask-kpis-app/data && chmod 666 /root/apps/flask-kpis-app/data/kpi_data.db` |
| Port 8502 already in use | Find conflicting container: `docker ps -a` |
| Health check failing | Test manually: `curl -v http://localhost:8502/health` |
| Image not found after build | Rebuild: `cd /root/lab/apps/flask_apps/kpis-app && docker build -t flask-kpi-dashboard .` |
| Login returns 500 error | Likely DB permission issue — check logs and fix permissions (see above) |
| Data directory missing | Recreate: `mkdir -p /root/apps/flask-kpis-app/data && chmod 777 /root/apps/flask-kpis-app/data` |
