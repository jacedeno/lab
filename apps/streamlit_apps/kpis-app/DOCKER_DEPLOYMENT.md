# Docker Deployment Guide for Weekly KPI Dashboard

This guide provides step-by-step instructions to deploy the Weekly KPI Dashboard using Docker.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
2. **Docker Compose** (optional, but recommended) - Usually comes with Docker Desktop

To verify installation:
```bash
docker --version
docker-compose --version
```

## Project Structure

Your project should have these files:
```
weekly-kpi-rev/
├── kpi.py                    # Main application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore           # Files to ignore in Docker build
└── assets/                 # Application assets
    ├── favicon.ico
    └── logo.png
```

## Deployment Methods

### Method 1: Using Docker Compose (Recommended)

Docker Compose simplifies the deployment process and makes it easier to manage.

#### Step 1: Navigate to Project Directory
```bash
cd /Users/geekendzone/weekly-kpi-rev
```

#### Step 2: Build and Run with Docker Compose
```bash
docker-compose up -d
```

This command will:
- Build the Docker image
- Start the container in detached mode (-d)
- Map port 8501 to your host machine
- Set up health checks

#### Step 3: Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8501
```

#### Step 4: View Logs (if needed)
```bash
docker-compose logs -f kpi-dashboard
```

#### Step 5: Stop the Application
```bash
docker-compose down
```

---

### Method 2: Using Docker Commands

If you prefer to use Docker commands directly without Docker Compose:

#### Step 1: Navigate to Project Directory
```bash
cd /Users/geekendzone/weekly-kpi-rev
```

#### Step 2: Build the Docker Image
```bash
docker build -t weekly-kpi-dashboard:latest .
```

#### Step 3: Run the Container
```bash
docker run -d \
  --name weekly-kpi-dashboard \
  -p 8501:8501 \
  --restart unless-stopped \
  weekly-kpi-dashboard:latest
```

#### Step 4: Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8501
```

#### Step 5: View Container Logs
```bash
docker logs -f weekly-kpi-dashboard
```

#### Step 6: Stop the Container
```bash
docker stop weekly-kpi-dashboard
```

#### Step 7: Remove the Container
```bash
docker rm weekly-kpi-dashboard
```

---

## Common Docker Commands

### Check Running Containers
```bash
docker ps
```

### Check All Containers (including stopped)
```bash
docker ps -a
```

### View Container Logs
```bash
# Docker Compose
docker-compose logs -f kpi-dashboard

# Docker
docker logs -f weekly-kpi-dashboard
```

### Restart the Application
```bash
# Docker Compose
docker-compose restart

# Docker
docker restart weekly-kpi-dashboard
```

### Rebuild After Code Changes
```bash
# Docker Compose
docker-compose up -d --build

# Docker
docker build -t weekly-kpi-dashboard:latest .
docker stop weekly-kpi-dashboard
docker rm weekly-kpi-dashboard
docker run -d --name weekly-kpi-dashboard -p 8501:8501 weekly-kpi-dashboard:latest
```

### Stop and Remove Everything
```bash
# Docker Compose
docker-compose down

# Docker
docker stop weekly-kpi-dashboard
docker rm weekly-kpi-dashboard
docker rmi weekly-kpi-dashboard:latest
```

---

## Deployment on Remote Server

To deploy on a remote server (e.g., AWS EC2, DigitalOcean, etc.):

### Step 1: Copy Files to Server
```bash
# Using scp
scp -r /Users/geekendzone/weekly-kpi-rev user@server-ip:/path/to/destination/

# Or use rsync
rsync -avz /Users/geekendzone/weekly-kpi-rev/ user@server-ip:/path/to/destination/
```

### Step 2: SSH into Server
```bash
ssh user@server-ip
```

### Step 3: Navigate to Project Directory
```bash
cd /path/to/destination/weekly-kpi-rev
```

### Step 4: Deploy with Docker Compose
```bash
docker-compose up -d
```

### Step 5: Configure Firewall (if needed)
```bash
# For Ubuntu/Debian with ufw
sudo ufw allow 8501/tcp

# For CentOS/RHEL with firewalld
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### Step 6: Access the Dashboard
```
http://server-ip:8501
```

---

## Production Deployment with Nginx (Optional)

For production, you may want to add Nginx as a reverse proxy:

### Step 1: Create nginx.conf
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 2: Update docker-compose.yml
Add Nginx service:
```yaml
services:
  kpi-dashboard:
    # ... existing configuration ...
    
  nginx:
    image: nginx:alpine
    container_name: kpi-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - kpi-dashboard
    restart: unless-stopped
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs kpi-dashboard

# Or
docker logs weekly-kpi-dashboard
```

### Port Already in Use
```bash
# Check what's using port 8501
lsof -i :8501

# Or use a different port
docker run -d --name weekly-kpi-dashboard -p 8502:8501 weekly-kpi-dashboard:latest
```

### Permission Errors
```bash
# On Linux, you might need sudo
sudo docker-compose up -d
```

### Image Build Fails
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

---

## Environment Variables

You can customize the deployment with environment variables:

```yaml
# In docker-compose.yml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## Data Persistence

**Note:** The current application stores data in session state, which means data is lost when the container restarts. For production use, consider implementing persistent storage using:

1. **Docker Volumes** for database
2. **External Database** (PostgreSQL, MySQL)
3. **File-based Storage** with mounted volumes

Example with volume:
```yaml
services:
  kpi-dashboard:
    volumes:
      - ./data:/app/data
```

---

## Health Checks

The container includes health checks. Monitor container health:

```bash
# Docker Compose
docker-compose ps

# Docker
docker inspect --format='{{.State.Health.Status}}' weekly-kpi-dashboard
```

---

## Security Recommendations

1. **Use HTTPS** in production (with Nginx + Let's Encrypt)
2. **Add Authentication** if needed (Streamlit supports basic auth)
3. **Update Dependencies** regularly
4. **Use Secrets** for sensitive data (not hardcoded)
5. **Limit Container Resources**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```

---

## Updating the Application

When you make changes to the code:

```bash
# Stop current container
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Or without Docker Compose
docker stop weekly-kpi-dashboard
docker rm weekly-kpi-dashboard
docker build -t weekly-kpi-dashboard:latest .
docker run -d --name weekly-kpi-dashboard -p 8501:8501 weekly-kpi-dashboard:latest
```

---

## Support

For issues or questions:
- Check the logs: `docker-compose logs -f`
- Verify Docker is running: `docker ps`
- Ensure port 8501 is available: `lsof -i :8501`

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start application |
| `docker-compose down` | Stop application |
| `docker-compose logs -f` | View logs |
| `docker-compose restart` | Restart application |
| `docker-compose up -d --build` | Rebuild and restart |
| `docker ps` | List running containers |
| `docker-compose ps` | List services status |

---

**Created by:** Jose Cedeno  
**Last Updated:** October 2025
