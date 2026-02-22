#!/bin/bash

# Kubernetes deployment script for Purchase Requisition app
# Usage: ./scripts/deploy.sh [options]
# Options:
#   --skip-postgres    Skip PostgreSQL deployment (if already running)
#   --skip-migrations  Skip running database migrations
#   --help             Show this help message

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
K8S_DIR="$PROJECT_ROOT/k8s"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
SKIP_POSTGRES=false
SKIP_MIGRATIONS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-postgres)
            SKIP_POSTGRES=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-postgres    Skip PostgreSQL deployment"
            echo "  --skip-migrations  Skip database migrations"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_step() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

wait_for_pods() {
    local selector=$1
    local namespace=$2
    local timeout=${3:-300}

    print_step "Waiting for pods to be ready (timeout: ${timeout}s)..."

    if kubectl wait --for=condition=ready pod -l "$selector" \
        -n "$namespace" --timeout="${timeout}s" 2>/dev/null; then
        print_success "Pods are ready"
        return 0
    else
        print_error "Timeout waiting for pods"
        echo "Current pod status:"
        kubectl get pods -n "$namespace" -l "$selector"
        return 1
    fi
}

# Verify prerequisites
print_header "Checking Prerequisites"

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl."
    exit 1
fi
print_success "kubectl found"

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi
print_success "Connected to Kubernetes cluster"

# Verify k8s manifests exist
if [ ! -d "$K8S_DIR" ]; then
    print_error "k8s directory not found at $K8S_DIR"
    exit 1
fi
print_success "k8s manifests directory found"

# Check required manifest files
for file in namespace.yaml secret.yaml configmap.yaml service.yaml deployment.yaml; do
    if [ ! -f "$K8S_DIR/$file" ]; then
        print_error "Missing manifest: $file"
        exit 1
    fi
done
print_success "All required manifests found"

# Main deployment
print_header "Creating Namespace"
print_step "Applying namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"
print_success "Namespace created/updated"

# PostgreSQL deployment
if [ "$SKIP_POSTGRES" = false ]; then
    print_header "Setting Up PostgreSQL"

    print_step "Installing CloudNativePG operator..."
    kubectl apply -f "$K8S_DIR/postgres/operator-install.yaml"
    print_success "Operator installed"

    print_step "Creating database credentials secret..."
    kubectl apply -f "$K8S_DIR/postgres/credentials.yaml"
    print_success "Credentials secret created"

    print_step "Creating PostgreSQL cluster..."
    kubectl apply -f "$K8S_DIR/postgres/cluster.yaml"
    print_success "PostgreSQL cluster created"

    # Wait for PostgreSQL to be ready
    print_step "Waiting for PostgreSQL to be ready..."
    if ! wait_for_pods "postgresql=instances" "purchase-requisition" 300; then
        print_error "PostgreSQL failed to start"
        echo ""
        echo "Debug info:"
        kubectl describe cnpg -n purchase-requisition pr-db 2>/dev/null || true
        exit 1
    fi
    print_success "PostgreSQL cluster is ready"
else
    print_step "Skipping PostgreSQL deployment (--skip-postgres)"
fi

# App deployment
print_header "Deploying Application"

print_step "Applying app secrets..."
kubectl apply -f "$K8S_DIR/secret.yaml"
print_success "Secrets applied"

print_step "Applying app config..."
kubectl apply -f "$K8S_DIR/configmap.yaml"
print_success "ConfigMap applied"

print_step "Applying service..."
kubectl apply -f "$K8S_DIR/service.yaml"
print_success "Service created"

print_step "Applying deployment..."
kubectl apply -f "$K8S_DIR/deployment.yaml"
print_success "Deployment created"

# Wait for app to be ready
print_step "Waiting for app pods to be ready..."
if ! wait_for_pods "app.kubernetes.io/name=purchase-requisition" "purchase-requisition" 120; then
    print_error "App pods failed to start"
    echo ""
    echo "Debug info:"
    kubectl describe pods -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition
    exit 1
fi
print_success "App pods are ready"

# Database migrations
if [ "$SKIP_MIGRATIONS" = false ]; then
    print_header "Running Database Migrations"

    print_step "Creating migration job..."
    kubectl apply -f "$K8S_DIR/migration-job.yaml"
    print_success "Migration job created"

    print_step "Waiting for migration job to complete..."
    kubectl wait --for=condition=complete job/pr-migration -n purchase-requisition --timeout=300s 2>/dev/null || {
        print_error "Migration job did not complete"
        echo ""
        echo "Migration logs:"
        kubectl logs -n purchase-requisition job/pr-migration --tail=50
        exit 1
    }
    print_success "Migrations completed"

    echo ""
    echo "Migration output:"
    kubectl logs -n purchase-requisition job/pr-migration --tail=20
else
    print_step "Skipping migrations (--skip-migrations)"
fi

# Verification
print_header "Deployment Verification"

echo ""
print_step "Pod status:"
kubectl get pods -n purchase-requisition
echo ""

print_step "Service status:"
kubectl get svc -n purchase-requisition
echo ""

print_step "Testing health endpoint inside cluster..."
if kubectl run -it --rm debug --image=curlimages/curl --restart=Never --quiet -- \
    curl -s http://pr-app.purchase-requisition.svc:80/health &>/dev/null; then
    print_success "Health check passed"
else
    print_error "Health check failed"
    echo "Trying to get more debug info..."
    kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
        curl -v http://pr-app.purchase-requisition.svc:80/health || true
fi

# Summary
print_header "Deployment Complete"

echo ""
echo -e "${GREEN}✓ Application deployed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure Cloudflare Tunnel:"
echo "     - Go to Cloudflare Dashboard → Zero Trust → Networks → Tunnels"
echo "     - Add public hostname: pr.capitolaggregates.com"
echo "     - Service: http://pr-app.purchase-requisition.svc.cluster.local:80"
echo ""
echo "  2. Configure Zero Trust Access:"
echo "     - Go to Cloudflare Dashboard → Zero Trust → Access → Applications"
echo "     - Create/Edit application for your domain"
echo "     - Allow email domain: @capitolaggregates.com"
echo ""
echo "  3. Test access:"
echo "     - Visit: https://pr.capitolaggregates.com"
echo "     - Authenticate with your @capitolaggregates.com email"
echo ""
echo "Useful commands:"
echo "  kubectl logs -n purchase-requisition -l app.kubernetes.io/name=purchase-requisition"
echo "  kubectl exec -it -n purchase-requisition <pod-name> -- /bin/bash"
echo "  kubectl port-forward -n purchase-requisition svc/pr-app 8000:80"
echo ""
