#!/bin/bash

# Build and push Docker image to private registry
# Usage: ./scripts/build-and-push.sh [registry-endpoint] [tag]
# Example: ./scripts/build-and-push.sh docker-registry.docker-registry.svc.cluster.local:5000 v1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Default values
REGISTRY="${1:-docker-registry.docker-registry.svc.cluster.local:5000}"
TAG="${2:-v1.0.0}"
IMAGE_NAME="purchase-requisition"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

print_step() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

echo ""
echo -e "${GREEN}=== Building and Pushing Docker Image ===${NC}"
echo "Registry: $REGISTRY"
echo "Image:    $IMAGE_NAME"
echo "Tag:      $TAG"
echo "Full:     $FULL_IMAGE"
echo ""

# Verify Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Make sure Docker is running."
    echo ""
    echo "Are you building on a node? Use nerdctl instead:"
    echo "  nerdctl build -t $FULL_IMAGE ."
    echo "  nerdctl push $FULL_IMAGE"
    exit 1
fi
print_success "Docker found"

# Verify Dockerfile exists
if [ ! -f "$PROJECT_ROOT/Dockerfile" ]; then
    print_error "Dockerfile not found in $PROJECT_ROOT"
    exit 1
fi
print_success "Dockerfile found"

echo ""

# Build image
print_step "Building image..."
cd "$PROJECT_ROOT"
docker build -t "$FULL_IMAGE" .

if [ $? -ne 0 ]; then
    print_error "Build failed"
    exit 1
fi
print_success "Image built successfully"

echo ""

# Push to registry
print_step "Pushing to registry..."
docker push "$FULL_IMAGE"

if [ $? -ne 0 ]; then
    print_error "Push failed"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check registry is accessible:"
    echo "     docker tag $FULL_IMAGE test && docker push test"
    echo "  2. Check Docker daemon config has insecure registry:"
    echo "     /etc/docker/daemon.json"
    echo ""
    exit 1
fi
print_success "Image pushed successfully"

echo ""
echo -e "${GREEN}=== Build and Push Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Update k8s/deployment.yaml line 25:"
echo "     image: $FULL_IMAGE"
echo ""
echo "  2. Deploy:"
echo "     ./scripts/deploy.sh"
echo ""
