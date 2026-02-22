# K3s Deployment Guide

This guide covers deploying the Purchase Requisition app to a k3s cluster.

## Prerequisites

- k3s cluster running and configured (kubeconfig available)
- Docker or Podman installed locally
- Container registry access (Docker Hub, private registry, etc.)
- CloudNativePG operator (for PostgreSQL HA)

## Step 1: Build and Push Docker Image

### Build the image:
```bash
docker build -t your-registry/purchase-requisition:v1.0.0 .
```

### Push to registry:
```bash
docker push your-registry/purchase-requisition:v1.0.0
```

### For local k3s without external registry (development only):
```bash
# Build and load directly into k3s
docker build -t purchase-requisition:latest .
# Or use: k3s ctr images import <image-tar-file>
```

## Step 2: Configure Secrets

Edit `k8s/secret.yaml` and set:

1. **DATABASE_URL**: PostgreSQL connection string
   ```
   postgresql://pr_user:STRONG_PASSWORD@pr-db-rw.purchase-requisition.svc:5432/purchase_requisition
   ```
   - Password must match `k8s/postgres/credentials.yaml`

2. **SECRET_KEY**: Flask secret key (generate a strong random string)
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **SMTP credentials** (optional, for email notifications)

## Step 3: Update Deployment Image Reference

Edit `k8s/deployment.yaml` line 25:

```yaml
image: your-registry/purchase-requisition:v1.0.0
# or for local development:
# image: purchase-requisition:latest
# imagePullPolicy: Never  # Add this for local images
```

## Step 4: Update Ingress Hostname

Edit `k8s/ingress.yaml` line 13:

```yaml
- host: pr.your-domain.com  # or your Cloudflare Tunnel hostname
```

## Step 5: Deploy PostgreSQL (if not already deployed)

### Install CloudNativePG operator:
```bash
kubectl apply -f k8s/postgres/operator-install.yaml
```

### Create PostgreSQL cluster:
```bash
kubectl apply -f k8s/postgres/credentials.yaml
kubectl apply -f k8s/postgres/cluster.yaml
```

### Wait for cluster to be ready:
```bash
kubectl wait --for=condition=ready pod -l postgresql=instances -n purchase-requisition --timeout=300s
```

## Step 6: Deploy the Application

### Create namespace and apply all manifests:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/deployment.yaml
```

### Or use Kustomize:
```bash
kubectl apply -k k8s/
```

### Run database migrations:
```bash
kubectl apply -f k8s/migration-job.yaml
kubectl logs -n purchase-requisition job/pr-migration --follow
```

## Step 7: Verify Deployment

### Check pod status:
```bash
kubectl get pods -n purchase-requisition
```

### Check ingress:
```bash
kubectl get ingress -n purchase-requisition
```

### View logs:
```bash
kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition
```

### Check service:
```bash
kubectl get svc -n purchase-requisition
```

## Step 8: Cloudflare Tunnel Configuration

If using Cloudflare Tunnel:

1. Route the tunnel to the ingress hostname:
   ```
   pr.your-domain.com → http://pr-app.purchase-requisition.svc.cluster.local
   ```

2. The app will receive email via `Cf-Access-Authenticated-User-Email` header from Cloudflare

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod -n purchase-requisition <pod-name>
```

### Database connection issues
```bash
# Verify PostgreSQL cluster is running
kubectl get cnpg -n purchase-requisition

# Test database connectivity from a pod
kubectl exec -it -n purchase-requisition <pod-name> -- \
  psql postgresql://pr_user:PASSWORD@pr-db-rw:5432/purchase_requisition
```

### Migration job failed
```bash
kubectl logs -n purchase-requisition job/pr-migration
```

### Ingress not working
```bash
kubectl describe ingress -n purchase-requisition pr-app
```

## Production Checklist

- [ ] Database credentials changed and secured
- [ ] Flask SECRET_KEY changed to strong random value
- [ ] Image pushed to private/secure registry
- [ ] PostgreSQL backup strategy configured
- [ ] SMTP credentials configured for notifications
- [ ] Cloudflare Tunnel configured and tested
- [ ] Resource limits reviewed for your cluster
- [ ] Monitoring/logging configured
