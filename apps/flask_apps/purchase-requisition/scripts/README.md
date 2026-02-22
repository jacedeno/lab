# Deployment Scripts

Automated scripts for building and deploying the Purchase Requisition app to Kubernetes.

## Quick Start

### 1. Build Docker Image

```bash
./scripts/build-image.sh
```

**Options:**

```bash
# Build with default tag (latest)
./scripts/build-image.sh

# Build and push to Docker Hub
./scripts/build-image.sh docker.io/youruser v1.0.0

# Build and push to private registry
./scripts/build-image.sh 192.168.1.100:5000 v1.0.0
```

**Output:**
- Local build: `purchase-requisition:latest` (or specified tag)
- Remote build: Also tags and pushes to registry

**Next:** If using a remote registry, update `k8s/deployment.yaml` with the full image path.

### 2. Load Image into k3s (Local Only)

If building for local k3s without pushing to registry:

```bash
docker save purchase-requisition:latest | k3s ctr images import /dev/stdin
```

Then in `k8s/deployment.yaml`, ensure:
```yaml
imagePullPolicy: Never
```

### 3. Deploy to Kubernetes

```bash
./scripts/deploy.sh
```

**What it does:**
1. ✅ Creates namespace
2. ✅ Installs CloudNativePG operator
3. ✅ Creates PostgreSQL cluster (waits for readiness)
4. ✅ Deploys app secrets and config
5. ✅ Deploys service and pods
6. ✅ Runs database migrations
7. ✅ Verifies all pods are running

**Options:**

```bash
# Skip PostgreSQL if already deployed
./scripts/deploy.sh --skip-postgres

# Skip database migrations
./scripts/deploy.sh --skip-migrations

# Skip both
./scripts/deploy.sh --skip-postgres --skip-migrations

# Show help
./scripts/deploy.sh --help
```

**Time to complete:** ~3-5 minutes (mostly waiting for PostgreSQL)

## Complete Workflow

### Step 1: Build Image

```bash
./scripts/build-image.sh
```

Or with registry:
```bash
./scripts/build-image.sh docker.io/myuser v1.0.0
```

### Step 2: Update Deployment (if using registry)

Edit `k8s/deployment.yaml` line 25:
```yaml
image: docker.io/myuser/purchase-requisition:v1.0.0
```

### Step 3: Deploy to k3s

```bash
./scripts/deploy.sh
```

Wait for completion (~3-5 minutes)

### Step 4: Configure Cloudflare Tunnel

1. Go to Cloudflare Dashboard → **Zero Trust → Networks → Tunnels**
2. Add public hostname:
   ```
   Domain:  pr.capitolaggregates.com
   Service: http://pr-app.purchase-requisition.svc.cluster.local:80
   ```

3. Configure Zero Trust Access:
   - Go to **Zero Trust → Access → Applications**
   - Create/Edit for `pr.capitolaggregates.com`
   - Allow emails with domain `@capitolaggregates.com`

### Step 5: Test

```bash
# Test health endpoint inside cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://pr-app.purchase-requisition.svc:80/health

# Access via browser
# Visit: https://pr.capitolaggregates.com
# Authenticate with @capitolaggregates.com email
```

## Other Scripts

### Cleanup (Delete Everything)

**WARNING: This deletes all resources including PostgreSQL data!**

```bash
./scripts/cleanup.sh

# Or force without confirmation
./scripts/cleanup.sh --force
```

This will:
1. Delete entire `purchase-requisition` namespace
2. Delete all pods, deployments, services, secrets, etc.
3. Delete PostgreSQL cluster and data

To redeploy: `./scripts/deploy.sh`

## Useful kubectl Commands

### View Logs

```bash
# Last 50 lines
kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition --tail=50

# Stream logs (follow)
kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition -f

# Migration logs
kubectl logs -n purchase-requisition job/pr-migration
```

### Inspect Resources

```bash
# Get all pods
kubectl get pods -n purchase-requisition

# Get services
kubectl get svc -n purchase-requisition

# Get PostgreSQL cluster status
kubectl get cnpg -n purchase-requisition

# Describe a pod
kubectl describe pod -n purchase-requisition <pod-name>
```

### Port Forward (for local testing)

```bash
# Forward port 8000 to app service
kubectl port-forward -n purchase-requisition svc/pr-app 8000:80

# Then visit: http://localhost:8000
```

### Execute Commands in Pod

```bash
# Get shell in pod
kubectl exec -it -n purchase-requisition <pod-name> -- /bin/bash

# Run command
kubectl exec -n purchase-requisition <pod-name> -- python wsgi.py
```

## Troubleshooting

### Image build fails

```bash
docker build -t purchase-requisition:latest .
```

Check:
- Dockerfile syntax
- All dependencies in requirements.txt
- File permissions

### Deployment fails

Check logs:
```bash
kubectl logs -n purchase-requisition job/pr-migration
kubectl describe pods -n purchase-requisition
```

### PostgreSQL not starting

```bash
kubectl get cnpg -n purchase-requisition
kubectl describe cnpg -n purchase-requisition pr-db
```

Common issues:
- Longhorn storage not available
- Not enough memory/CPU
- Network policies blocking traffic

### App pods not starting

```bash
kubectl describe pod -n purchase-requisition <pod-name>
kubectl logs -n purchase-requisition <pod-name>
```

Common issues:
- Image not found (check imagePullPolicy)
- Database not ready
- Secrets missing

### Health check fails

```bash
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -v http://pr-app.purchase-requisition.svc:80/health
```

## Script Requirements

- `bash` shell
- `kubectl` (configured and connected to cluster)
- `docker` (for building images)
- Kubernetes cluster with:
  - CloudNativePG operator
  - Storage provisioner (Longhorn, local-path, etc)
  - Sufficient resources (recommend 2+ nodes with 2GB RAM each)

## Environment

Scripts automatically detect:
- Kubernetes cluster connection
- Project root directory
- k8s manifest files

No configuration needed if run from project root.

## Notes

- All scripts are idempotent (safe to run multiple times)
- Scripts validate prerequisites before running
- Detailed output for debugging
- Colors for easy reading
- Automatic timeouts to prevent hanging

## For More Information

See documentation:
- `docs/DEPLOYMENT_CHECKLIST.md` - Manual deployment steps
- `docs/CLOUDFLARE_TUNNEL.md` - Cloudflare Tunnel configuration
- `docs/MANAGING_BUYERS.md` - How to manage buyer list
