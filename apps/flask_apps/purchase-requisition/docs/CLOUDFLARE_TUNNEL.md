# Cloudflare Tunnel Configuration Guide

Instead of using Kubernetes Ingress, you can expose the app using Cloudflare Tunnel (cloudflared). This is simpler and you don't need DNS changes.

## How Cloudflare Tunnel Works

```
Internet (Your Domain)
    ↓
Cloudflare Edge
    ↓
Cloudflare Tunnel (cloudflared) running in your cluster
    ↓
Service: pr-app.purchase-requisition.svc.cluster.local:80
    ↓
Pods running Flask app
```

## Prerequisites

1. Cloudflare account with a domain
2. Cloudflare Tunnel already configured and running in your cluster
3. `cloudflared` CLI installed locally

## Step 1: Verify Cloudflare Tunnel is Running

```bash
# Check if cloudflared is deployed
kubectl get pods -n kube-system | grep cloudflare

# Or check for the tunnel pod
kubectl get pods -A | grep cloudflare
```

If not installed, follow your cluster's Cloudflare Tunnel setup (usually via Helm or manual deployment).

## Step 2: Create Tunnel Route in Cloudflare Dashboard

1. Go to **Cloudflare Dashboard → Zero Trust → Networks → Tunnels**
2. Find your tunnel configuration
3. Add a new route:
   ```
   Public Hostname:  pr.capitolaggregates.com  (or your domain)
   Service:          http://pr-app.purchase-requisition.svc.cluster.local:80
   ```

Alternative: Using `cloudflared` CLI:

```bash
cloudflared tunnel route dns <tunnel-name> pr.capitolaggregates.com
```

## Step 3: Deploy the App Without Ingress

Since you're using Cloudflare Tunnel, **you don't need the Ingress manifest**.

Deploy only:

```bash
# Create namespace and deploy app
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/operator-install.yaml
kubectl apply -f k8s/postgres/credentials.yaml
kubectl apply -f k8s/postgres/cluster.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l postgresql=instances \
  -n purchase-requisition --timeout=300s

# Deploy the app (NO ingress.yaml)
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml

# Run migrations
kubectl apply -f k8s/migration-job.yaml
kubectl logs -n purchase-requisition job/pr-migration --follow
```

## Step 4: Verify Access

1. **Check service is running:**
   ```bash
   kubectl get svc -n purchase-requisition
   ```
   You should see `pr-app` with ClusterIP (not LoadBalancer)

2. **Check pods are ready:**
   ```bash
   kubectl get pods -n purchase-requisition
   ```
   All pod statuses should be `Running`

3. **Test from inside cluster:**
   ```bash
   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
     curl http://pr-app.purchase-requisition.svc.cluster.local:80/health
   ```
   Should return `200 OK`

4. **Access via Cloudflare Tunnel:**
   - Visit: `https://pr.capitolaggregates.com`
   - Should load the app

## Step 5: Cloudflare Zero Trust Authentication

The app relies on Cloudflare to inject the user email via header:

```
Cf-Access-Authenticated-User-Email: user@capitolaggregates.com
```

Configure in **Cloudflare Dashboard → Zero Trust → Access → Applications:**

1. Create or edit your application for `pr.capitolaggregates.com`
2. Set policy to allow users with:
   - **Email domain matches** `@capitolaggregates.com`
   - OR specific email addresses
3. Cloudflare will automatically authenticate and inject the email header

## Troubleshooting

### App not accessible via tunnel

1. **Check cloudflared is connected:**
   ```bash
   cloudflared tunnel status
   ```

2. **Verify service is reachable inside cluster:**
   ```bash
   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
     curl http://pr-app.purchase-requisition.svc:80/health
   ```

3. **Check pod logs:**
   ```bash
   kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition
   ```

4. **Verify Cloudflare route:**
   - Check tunnel config has correct service URL
   - Make sure public hostname matches your domain

### Users getting 403 Forbidden

- Check Cloudflare Zero Trust policy allows their email domain
- Verify they're using an email with @capitolaggregates.com

### Database connection errors

```bash
# Test PostgreSQL connectivity
kubectl exec -it -n purchase-requisition <pod-name> -- \
  psql postgresql://pr_user:PASSWORD@pr-db-rw:5432/purchase_requisition \
  -c "SELECT 1"
```

## No Ingress Needed

Since Cloudflare Tunnel handles routing, **delete or ignore** `k8s/ingress.yaml`.

The service type remains `ClusterIP` because the tunnel accesses it internally.

## Summary

✅ Service: `ClusterIP` (only cluster-internal access)
✅ Cloudflare Tunnel: Routes external traffic
✅ Zero Trust: Cloudflare authenticates users
✅ No public port exposure needed
✅ No Ingress controller required
