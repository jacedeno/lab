# Private Docker Registry Setup

Complete guide for setting up and using a private Docker registry in your k3s cluster following DevOps best practices.

## Architecture

```
Your Workstation (with Docker)
    ↓ (build & push)
Private Registry (in cluster)
    ↓ (pull)
k3s Cluster Nodes
    ↓ (run)
Purchase Requisition Pods
```

## Prerequisites

- kubectl configured and connected to k3s cluster
- Docker installed on your workstation (for building images)
- Longhorn storage available (for registry persistence)

## Step 1: Deploy Private Registry to Cluster

The registry will run inside your k3s cluster with persistent storage via Longhorn.

```bash
./scripts/setup-registry.sh
```

**What it does:**
1. Creates `docker-registry` namespace
2. Creates 20Gi Longhorn PVC for persistence
3. Deploys Docker Registry v2
4. Creates ClusterIP service
5. Waits for registry pod to be ready

**Time:** ~2-3 minutes

**Verify it's running:**
```bash
kubectl get pods -n docker-registry
kubectl get svc -n docker-registry
```

**Expected output:**
- Pod: `docker-registry-xxx` in `Running` state
- Service: `docker-registry` with ClusterIP `10.43.x.x`

---

## Step 2: Configure Docker on Your Workstation

The registry is accessible at:
```
docker-registry.docker-registry.svc.cluster.local:5000
```

However, Docker needs to know it's an insecure registry (no HTTPS). Configure it:

**On macOS:**
1. Docker Desktop → Preferences → Docker Engine
2. Add to `daemon.json`:
   ```json
   {
     "insecure-registries": [
       "docker-registry.docker-registry.svc.cluster.local:5000"
     ]
   }
   ```
3. Click "Apply & Restart"

**On Linux:**
1. Edit `/etc/docker/daemon.json`
2. Add:
   ```json
   {
     "insecure-registries": [
       "docker-registry.docker-registry.svc.cluster.local:5000"
     ]
   }
   ```
3. Restart Docker:
   ```bash
   sudo systemctl restart docker
   ```

---

## Step 3: Build and Push Image to Registry

### From Your Workstation

```bash
./scripts/build-and-push.sh
```

**Or manually:**

```bash
cd /path/to/purchase-requisition

# Build
docker build -t docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:v1.0.0 .

# Push
docker push docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:v1.0.0
```

**Troubleshooting:**

If Docker can't resolve the registry hostname:

**Option A: Port-forward to registry (from another terminal)**
```bash
kubectl port-forward -n docker-registry svc/docker-registry 5000:5000 &
```

Then use `localhost:5000`:
```bash
docker build -t localhost:5000/purchase-requisition:v1.0.0 .
docker push localhost:5000/purchase-requisition:v1.0.0
```

And update `k8s/deployment.yaml`:
```yaml
image: localhost:5000/purchase-requisition:v1.0.0
```

**Option B: SSH to master and use nerdctl**

```bash
ssh root@192.168.30.10

# Copy repo if needed
scp -r /path/to/purchase-requisition root@192.168.30.10:/tmp/

# On master, build with nerdctl
cd /tmp/purchase-requisition
nerdctl build -t docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:v1.0.0 .
nerdctl push docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:v1.0.0
```

---

## Step 4: Deploy Application

The `k8s/deployment.yaml` is already configured to use the registry:

```yaml
image: docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:v1.0.0
```

Deploy:
```bash
./scripts/deploy.sh
```

Or manually:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/operator-install.yaml
kubectl apply -f k8s/postgres/credentials.yaml
kubectl apply -f k8s/postgres/cluster.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/migration-job.yaml
```

---

## Step 5: Verify Registry

### Check image in registry

From your workstation, if using port-forward:

```bash
# In another terminal
kubectl port-forward -n docker-registry svc/docker-registry 5000:5000 &

# Then
curl http://localhost:5000/v2/_catalog
```

Expected response:
```json
{
  "repositories": [
    "purchase-requisition"
  ]
}
```

### List tags

```bash
curl http://localhost:5000/v2/purchase-requisition/tags/list
```

### View registry logs

```bash
kubectl logs -n docker-registry -l app.kubernetes.io/name=docker-registry -f
```

---

## Registry Storage

The registry uses Longhorn for persistence. To check storage usage:

```bash
kubectl get pvc -n docker-registry
kubectl get pv
```

**To resize:**
```bash
kubectl edit pvc registry-storage -n docker-registry
# Change spec.resources.requests.storage to desired size
```

---

## Best Practices Implemented

✅ **Private Registry** - Images stored in cluster, not external
✅ **Persistent Storage** - Data survives pod restarts
✅ **Namespace Isolation** - Registry in separate namespace
✅ **Resource Limits** - Registry has CPU/memory constraints
✅ **Service Discovery** - Uses internal DNS names
✅ **Simple to Use** - Single script to setup and deploy

---

## Future Enhancements

- Add HTTPS with self-signed certificate
- Add basic authentication
- Enable garbage collection for old images
- Add registry UI dashboard
- Setup image scanning/vulnerability checks

---

## Cleanup

If you need to remove the registry:

```bash
kubectl delete namespace docker-registry
```

This will delete all images! Make sure you have backups if needed.

---

## Troubleshooting

### Registry pod not starting

```bash
kubectl describe pod -n docker-registry docker-registry-xxx
kubectl logs -n docker-registry docker-registry-xxx
```

Common issues:
- Longhorn not available → check `kubectl get storageclass`
- PVC stuck in pending → check Longhorn status

### Can't push image

```bash
# Test registry connectivity
docker ping docker-registry.docker-registry.svc.cluster.local:5000

# If DNS not resolving, use port-forward instead
kubectl port-forward -n docker-registry svc/docker-registry 5000:5000
docker push localhost:5000/purchase-requisition:v1.0.0
```

### Image pull fails on nodes

```bash
# Check if nodes can access registry
kubectl run -it --rm debug --image=alpine --restart=Never -- \
  wget http://docker-registry.docker-registry.svc.cluster.local:5000/v2/_catalog

# Check pod events
kubectl describe pod -n purchase-requisition <pod-name>
```

---

## Related Documentation

- `docs/DEPLOYMENT_CHECKLIST.md` - Manual deployment steps
- `docs/CLOUDFLARE_TUNNEL.md` - Network exposure
- `docs/K3S_DEPLOYMENT.md` - Kubernetes deployment guide
