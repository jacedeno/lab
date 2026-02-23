#!/bin/bash

# Configure k3s nodes to use the private Docker registry over HTTP
# Usage: ./scripts/configure-registry-nodes.sh [ssh-user]
# Example: ./scripts/configure-registry-nodes.sh geekendzone

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SSH_USER="${1:-geekendzone}"

# Get registry ClusterIP
REGISTRY_IP=$(kubectl get svc -n docker-registry docker-registry -o jsonpath='{.spec.clusterIP}')

if [ -z "$REGISTRY_IP" ]; then
    echo -e "${RED}✗ Could not get registry ClusterIP. Is the registry deployed?${NC}"
    exit 1
fi

echo -e "${BLUE}=== Configuring k3s Nodes for Private Registry ===${NC}"
echo "Registry ClusterIP: $REGISTRY_IP"
echo "SSH User: $SSH_USER"
echo ""

# Get all node IPs
NODES=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')

REGISTRIES_CONTENT="mirrors:
  \"docker-registry.docker-registry.svc.cluster.local:5000\":
    endpoint:
      - \"http://${REGISTRY_IP}:5000\"
"

for NODE_IP in $NODES; do
    NODE_NAME=$(kubectl get nodes -o wide | grep "$NODE_IP" | awk '{print $1}')
    echo -e "${YELLOW}→ Configuring $NODE_NAME ($NODE_IP)...${NC}"

    # Copy registries.yaml to node
    ssh "$SSH_USER@$NODE_IP" "echo '$REGISTRIES_CONTENT' | sudo tee /etc/rancher/k3s/registries.yaml > /dev/null"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ registries.yaml written${NC}"
    else
        echo -e "${RED}  ✗ Failed to write registries.yaml${NC}"
        continue
    fi

    # Restart k3s on this node
    if ssh "$SSH_USER@$NODE_IP" "systemctl is-active k3s.service" &>/dev/null; then
        # This is the master (runs k3s server)
        ssh "$SSH_USER@$NODE_IP" "sudo systemctl restart k3s"
        echo -e "${GREEN}  ✓ k3s server restarted${NC}"
    elif ssh "$SSH_USER@$NODE_IP" "systemctl is-active k3s-agent.service" &>/dev/null; then
        # This is a worker (runs k3s agent)
        ssh "$SSH_USER@$NODE_IP" "sudo systemctl restart k3s-agent"
        echo -e "${GREEN}  ✓ k3s agent restarted${NC}"
    else
        echo -e "${RED}  ✗ Could not determine k3s service type${NC}"
    fi

    echo ""
done

echo -e "${BLUE}=== Waiting for all nodes to rejoin cluster ===${NC}"
sleep 15

kubectl get nodes
echo ""

echo -e "${GREEN}=== Configuration Complete ===${NC}"
echo ""
echo "All nodes are now configured to pull from the private registry."
echo ""
echo "Next: Restart the app deployment to trigger a new image pull:"
echo "  kubectl rollout restart deployment/pr-app -n purchase-requisition"
echo ""
