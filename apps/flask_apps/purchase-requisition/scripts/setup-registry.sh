#!/bin/bash

# Setup Private Docker Registry in k3s cluster
# Usage: ./scripts/setup-registry.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
K8S_DIR="$PROJECT_ROOT/k8s"

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

# Verify prerequisites
print_header "Checking Prerequisites"

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found"
    exit 1
fi
print_success "kubectl found"

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi
print_success "Connected to cluster"

# Deploy registry
print_header "Setting Up Private Docker Registry"

print_step "Creating namespace..."
kubectl apply -f "$K8S_DIR/registry/namespace.yaml"
print_success "Namespace created"

print_step "Creating persistent volume claim..."
kubectl apply -f "$K8S_DIR/registry/pvc.yaml"
print_success "PVC created"

print_step "Deploying registry..."
kubectl apply -f "$K8S_DIR/registry/deployment.yaml"
print_success "Deployment created"

print_step "Creating service..."
kubectl apply -f "$K8S_DIR/registry/service.yaml"
print_success "Service created"

# Wait for registry to be ready
print_step "Waiting for registry pod to be ready..."
if kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=docker-registry \
    -n docker-registry --timeout=120s 2>/dev/null; then
    print_success "Registry is ready"
else
    print_error "Timeout waiting for registry"
    exit 1
fi

# Get registry endpoint
REGISTRY_ENDPOINT="docker-registry.docker-registry.svc.cluster.local:5000"

print_header "Registry Setup Complete"

echo ""
echo -e "${GREEN}✓ Private registry is running!${NC}"
echo ""
echo "Registry endpoint: $REGISTRY_ENDPOINT"
echo ""
echo "To use the registry:"
echo ""
echo "  1. Build your image:"
echo "     docker build -t $REGISTRY_ENDPOINT/purchase-requisition:v1.0.0 ."
echo ""
echo "  2. Push to registry:"
echo "     docker push $REGISTRY_ENDPOINT/purchase-requisition:v1.0.0"
echo ""
echo "  3. In k8s/deployment.yaml, set:"
echo "     image: $REGISTRY_ENDPOINT/purchase-requisition:v1.0.0"
echo ""
echo "  4. Deploy:"
echo "     ./scripts/deploy.sh"
echo ""
echo "Useful commands:"
echo "  kubectl logs -n docker-registry -l app.kubernetes.io/name=docker-registry"
echo "  kubectl port-forward -n docker-registry svc/docker-registry 5000:5000"
echo ""
