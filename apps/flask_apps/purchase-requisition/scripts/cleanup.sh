#!/bin/bash

# Cleanup script for Purchase Requisition app deployment
# WARNING: This deletes all resources in the purchase-requisition namespace
# Usage: ./scripts/cleanup.sh [--force]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FORCE=false
NAMESPACE="purchase-requisition"

# Parse arguments
if [ "$1" == "--force" ]; then
    FORCE=true
fi

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Show warning
echo ""
print_warning "This will delete ALL resources in namespace: $NAMESPACE"
print_warning "This includes:"
print_warning "  - All pods and deployments"
print_warning "  - PostgreSQL cluster and data"
print_warning "  - Secrets and ConfigMaps"
print_warning "  - Services"
echo ""
print_warning "This action CANNOT be undone!"
echo ""

if [ "$FORCE" != true ]; then
    read -p "Are you absolutely sure? Type 'yes' to confirm: " confirmation
    if [ "$confirmation" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "Starting cleanup..."
echo ""

# Delete namespace (this deletes everything in it)
echo "Deleting namespace $NAMESPACE..."
if kubectl delete namespace "$NAMESPACE" --ignore-not-found=true; then
    print_success "Namespace deleted"
else
    print_error "Failed to delete namespace"
    exit 1
fi

echo ""
echo "Waiting for namespace deletion..."
kubectl wait --for=delete namespace/"$NAMESPACE" --timeout=60s 2>/dev/null || true

echo ""
print_success "Cleanup complete"
echo ""
echo "To redeploy, run: ./scripts/deploy.sh"
