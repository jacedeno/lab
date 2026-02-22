#!/bin/bash

# Build Docker image script for Purchase Requisition app
# Usage: ./scripts/build-image.sh [registry] [tag]
# Examples:
#   ./scripts/build-image.sh                    (local: purchase-requisition:latest)
#   ./scripts/build-image.sh docker.io/myuser v1.0.0
#   ./scripts/build-image.sh 192.168.1.100:5000 v1.0.0

set -e

# Configuration
REGISTRY="${1:-}"
TAG="${2:-latest}"
IMAGE_NAME="purchase-requisition"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Building Docker Image ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Image name: $IMAGE_NAME"
echo "Tag: $TAG"
[ -n "$REGISTRY" ] && echo "Registry: $REGISTRY"
echo ""

# Verify Dockerfile exists
if [ ! -f "$PROJECT_ROOT/Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found in $PROJECT_ROOT${NC}"
    exit 1
fi

# Build the image
echo -e "${YELLOW}Building image...${NC}"
cd "$PROJECT_ROOT"
docker build -t "$IMAGE_NAME:$TAG" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image built successfully${NC}"
    echo ""
    echo "Image: $IMAGE_NAME:$TAG"
    docker images | grep "$IMAGE_NAME" | head -1
else
    echo -e "${RED}✗ Image build failed${NC}"
    exit 1
fi

# If registry specified, tag and push
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"
    echo ""
    echo -e "${YELLOW}Tagging image for registry...${NC}"
    docker tag "$IMAGE_NAME:$TAG" "$FULL_IMAGE"
    echo -e "${GREEN}✓ Tagged as: $FULL_IMAGE${NC}"

    echo ""
    echo -e "${YELLOW}Pushing to registry...${NC}"
    docker push "$FULL_IMAGE"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Pushed successfully${NC}"
        echo ""
        echo -e "${YELLOW}UPDATE k8s/deployment.yaml line 25:${NC}"
        echo "  image: $FULL_IMAGE"
    else
        echo -e "${RED}✗ Push failed${NC}"
        exit 1
    fi
else
    echo ""
    echo -e "${YELLOW}For local k3s deployment, load the image:${NC}"
    echo "  docker save $IMAGE_NAME:$TAG | k3s ctr images import /dev/stdin"
    echo ""
    echo -e "${YELLOW}Or set imagePullPolicy in k8s/deployment.yaml:${NC}"
    echo "  image: $IMAGE_NAME:$TAG"
    echo "  imagePullPolicy: Never"
fi

echo ""
echo -e "${GREEN}=== Build Complete ===${NC}"
