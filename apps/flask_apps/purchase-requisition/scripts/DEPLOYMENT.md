# Deployment Guide — Purchase Requisition App

## Overview

This app runs on a K3s cluster with 4 nodes:

| Node | Role | IP |
|------|------|----|
| k3s-master | control-plane | 192.168.30.10 |
| k3s-worker1 | worker | 192.168.30.11 |
| k3s-worker2 | worker | 192.168.30.12 |
| k3s-worker3 | worker | 192.168.30.13 |

Images are built locally with **Podman** and imported directly into each node's containerd runtime via `k3s ctr images import`. There is no working Docker registry push from the workstation.

---

## Step-by-Step: Build, Deploy, and Rollout

### 1. Build the image

From the project root on your workstation:

```bash
cd /home/geekendzone/lab/apps/flask_apps/purchase-requisition
podman build -t docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:vX.Y.Z .
```

Replace `vX.Y.Z` with the new version tag (e.g., `v1.2.0`).

### 2. Save the image to a tar file

```bash
podman save docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:vX.Y.Z -o /tmp/pr-vX.Y.Z.tar
```

> If you get `docker-archive doesn't support modifying existing images`, delete the old tar first: `rm /tmp/pr-vX.Y.Z.tar`

### 3. Copy the tar to ALL nodes (master + workers)

```bash
scp /tmp/pr-vX.Y.Z.tar geekendzone@192.168.30.10:/tmp/
scp /tmp/pr-vX.Y.Z.tar geekendzone@192.168.30.11:/tmp/
scp /tmp/pr-vX.Y.Z.tar geekendzone@192.168.30.12:/tmp/
scp /tmp/pr-vX.Y.Z.tar geekendzone@192.168.30.13:/tmp/
```

> **IMPORTANT:** You must copy to ALL 4 nodes (including master). K8s can schedule pods on any node. If a node doesn't have the image, pods will fail with `ImagePullBackOff`.

### 4. Import the image on each node

SSH into **each** node individually and run:

```bash
sudo k3s ctr images import /tmp/pr-vX.Y.Z.tar
```

> `ssh geekendzone@<ip> "sudo ..."` does not work because sudo requires a TTY for password input. You must SSH in interactively.

After importing, clean up the tar:

```bash
rm /tmp/pr-vX.Y.Z.tar
```

### 5. Update K8s manifests

Update the image tag in these files:

- `k8s/deployment.yaml` — line with `image:`
- `k8s/migration-job.yaml` — line with `image:`

Both should point to the new tag:

```yaml
image: docker-registry.docker-registry.svc.cluster.local:5000/purchase-requisition:vX.Y.Z
```

### 6. Apply secrets and config (if changed)

```bash
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
```

### 7. Run database migrations

```bash
kubectl delete job pr-app-migrate -n purchase-requisition --ignore-not-found
kubectl apply -f k8s/migration-job.yaml
```

Verify migration completed:

```bash
kubectl wait --for=condition=complete job/pr-app-migrate -n purchase-requisition --timeout=120s
kubectl logs -n purchase-requisition job/pr-app-migrate
```

### 8. Deploy / Rollout

If you updated the image tag in `deployment.yaml`:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/pr-app -n purchase-requisition
```

If the image tag is the same but the image contents changed (rebuilt same tag):

```bash
kubectl rollout restart deployment/pr-app -n purchase-requisition
kubectl rollout status deployment/pr-app -n purchase-requisition
```

---

## Troubleshooting

### Check pod status

```bash
kubectl get pods -n purchase-requisition -o wide
```

### Check app logs

```bash
kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition --tail=50
```

### Check a specific pod's logs

```bash
kubectl logs -n purchase-requisition <pod-name> --tail=100
```

### ImagePullBackOff error

The image was not imported on the node where the pod was scheduled. Check which node:

```bash
kubectl get pod -n purchase-requisition <pod-name> -o wide
```

Then SSH into that node and import the image.

### Migration job stuck

```bash
kubectl describe job pr-app-migrate -n purchase-requisition
kubectl get pod -n purchase-requisition -l app.kubernetes.io/component=migration -o wide
```

Delete and retry:

```bash
kubectl delete job pr-app-migrate -n purchase-requisition --ignore-not-found
kubectl apply -f k8s/migration-job.yaml
```

### Rollback to previous version

```bash
kubectl rollout undo deployment/pr-app -n purchase-requisition
kubectl rollout status deployment/pr-app -n purchase-requisition
```

### Check which image is currently running

```bash
kubectl get deployment pr-app -n purchase-requisition -o jsonpath='{.spec.template.spec.containers[0].image}'
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Build image | `podman build -t ...:vX.Y.Z .` |
| Save image | `podman save ...:vX.Y.Z -o /tmp/pr-vX.Y.Z.tar` |
| Import on node | `sudo k3s ctr images import /tmp/pr-vX.Y.Z.tar` |
| Apply deployment | `kubectl apply -f k8s/deployment.yaml` |
| Restart pods (same tag) | `kubectl rollout restart deployment/pr-app -n purchase-requisition` |
| Check rollout | `kubectl rollout status deployment/pr-app -n purchase-requisition` |
| View logs | `kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition --tail=50` |
| Run migration | `kubectl delete job pr-app-migrate -n purchase-requisition --ignore-not-found && kubectl apply -f k8s/migration-job.yaml` |
| Rollback | `kubectl rollout undo deployment/pr-app -n purchase-requisition` |
