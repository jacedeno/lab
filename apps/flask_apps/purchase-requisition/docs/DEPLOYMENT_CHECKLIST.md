# Deployment Checklist

This is your step-by-step checklist for deploying to k3s with Cloudflare Tunnel.

## ✅ Step 1: Credentials Already Generated and Configured

**Status**: ✅ DONE

- Database password: Set in `k8s/postgres/credentials.yaml`
- Flask SECRET_KEY: Set in `k8s/secret.yaml`
- DATABASE_URL: Configured in `k8s/secret.yaml`

**What was set:**
```
DB Password:     XU3Fx_Ea7zTy6yWW7BfAl1uzz2Z3UTORhfQgHKWfYrA
Flask SECRET:    a705c11289c31b610ba4fbe735838837c22d2a22829d05d29d98bf6fe46b34d2
```

---

## ✅ Step 2: Build Docker Image

**Status**: ⏳ YOU DO THIS

Run this on your machine:

```bash
cd /path/to/purchase-requisition

# Build the image
docker build -t purchase-requisition:v1.0.0 .

# Option A: Load into local k3s (if running locally)
docker save purchase-requisition:v1.0.0 | k3s ctr images import /dev/stdin

# Option B: Push to registry (if using remote registry)
docker tag purchase-requisition:v1.0.0 docker.io/youruser/purchase-requisition:v1.0.0
docker push docker.io/youruser/purchase-requisition:v1.0.0
```

**Then update** `k8s/deployment.yaml` line 25:
- For local k3s: `image: purchase-requisition:v1.0.0` + `imagePullPolicy: Never`
- For registry: `image: docker.io/youruser/purchase-requisition:v1.0.0`

---

## ✅ Step 3: Deploy to K3s

Run these commands on your cluster:

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Install and create PostgreSQL
kubectl apply -f k8s/postgres/operator-install.yaml
kubectl apply -f k8s/postgres/credentials.yaml
kubectl apply -f k8s/postgres/cluster.yaml

# 3. Wait for PostgreSQL to be ready (takes 1-2 min)
kubectl wait --for=condition=ready pod -l postgresql=instances \
  -n purchase-requisition --timeout=300s

# 4. Deploy the app secrets and config
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml

# 5. Deploy the service and app
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml

# 6. Run database migrations
kubectl apply -f k8s/migration-job.yaml

# 7. Check migration logs
kubectl logs -n purchase-requisition job/pr-migration -f
```

**Verify everything is running:**
```bash
kubectl get pods -n purchase-requisition
kubectl get svc -n purchase-requisition
```

All pods should be `Running` or `Completed`.

---

## ✅ Step 4: Configure Cloudflare Tunnel

**Status**: ⏳ YOU DO THIS

Since your Cloudflare Tunnel is already running in the cluster:

### In Cloudflare Dashboard:

1. Go: **Zero Trust → Networks → Tunnels**
2. Click your tunnel
3. Add a **Public Hostname** route:
   ```
   Domain:   pr.capitolaggregates.com  (or your domain)
   Service:  http://pr-app.purchase-requisition.svc.cluster.local:80
   ```

### Configure Zero Trust Access:

1. Go: **Zero Trust → Access → Applications**
2. Create/Edit application for `pr.capitolaggregates.com`
3. Set policy to allow emails with domain `@capitolaggregates.com`
4. Save

---

## ✅ Step 5: Test Access

**Status**: ⏳ YOU DO THIS

1. **Inside cluster** (verify service works):
   ```bash
   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
     curl http://pr-app.purchase-requisition.svc:80/health
   ```
   Should return: `200 OK`

2. **Via Cloudflare Tunnel** (from internet):
   - Visit: `https://pr.capitolaggregates.com`
   - You should see the login/requisition form
   - Cloudflare will ask for your email authentication
   - Enter your `@capitolaggregates.com` email
   - You should be logged in as a Requester
   - If your email is in `app/config/buyers.yaml`, you'll see Buyer features too

---

## 🎯 Key Points

### You DON'T need:
- ❌ Kubernetes Ingress (Cloudflare Tunnel replaces it)
- ❌ External DNS changes
- ❌ To open ports on your firewall
- ❌ TLS certificates (Cloudflare handles this)

### You DO have:
- ✅ Automatic email authentication via Cloudflare
- ✅ HTTPS by default
- ✅ HA PostgreSQL (3 replicas)
- ✅ All traffic through secure Cloudflare tunnel

---

## 📝 Important Files Modified

All credentials and configs are already set in:
- ✅ `k8s/postgres/credentials.yaml` - DB password
- ✅ `k8s/secret.yaml` - Flask SECRET_KEY + DATABASE_URL
- ✅ `k8s/configmap.yaml` - App config (BUYER_EMAILS removed)
- ✅ `k8s/deployment.yaml` - Updated image reference placeholder

---

## ❓ Troubleshooting

### Pods not starting?
```bash
kubectl describe pod -n purchase-requisition <pod-name>
```

### PostgreSQL not ready?
```bash
kubectl get cnpg -n purchase-requisition
```

### Can't access app via Cloudflare?
- Verify tunnel route in Cloudflare dashboard
- Check pod logs: `kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition`
- Test inside cluster: `kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://pr-app.purchase-requisition.svc:80/health`

### Users getting 403?
- Check Cloudflare Zero Trust policy allows `@capitolaggregates.com` emails

---

## Next: What's Left?

1. ⏳ Build Docker image (on your machine)
2. ⏳ Deploy to k3s (copy/paste commands above)
3. ⏳ Configure Cloudflare Tunnel route
4. ⏳ Test access from browser
5. ✅ All else is done!

Questions? See:
- `docs/CLOUDFLARE_TUNNEL.md` - Tunnel config details
- `docs/MANAGING_BUYERS.md` - How to add/remove buyers
