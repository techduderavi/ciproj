#!/bin/bash

# Script to switch between blue and green deployments in Kubernetes

# Check current traffic distribution
echo "Current traffic distribution:"
kubectl get ingress app-ingress-canary -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}'

# Prompt for deployment choice
echo ""
echo "Choose deployment option:"
echo "1. Blue (100%)"
echo "2. Green (100%)"
echo "3. Canary (Blue 90%, Green 10%)"
echo "4. 50/50 Split"
read -p "Enter choice (1-4): " choice

case $choice in
  1)
    # 100% Blue
    kubectl annotate ingress app-ingress-canary nginx.ingress.kubernetes.io/canary-weight=0 --overwrite
    ;;
  2)
    # 100% Green (by making the canary weight 100)
    kubectl annotate ingress app-ingress-canary nginx.ingress.kubernetes.io/canary-weight=100 --overwrite
    ;;
  3)
    # Canary (90% Blue, 10% Green)
    kubectl annotate ingress app-ingress-canary nginx.ingress.kubernetes.io/canary-weight=10 --overwrite
    ;;
  4)
    # 50/50 Split
    kubectl annotate ingress app-ingress-canary nginx.ingress.kubernetes.io/canary-weight=50 --overwrite
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "Deployment updated. New traffic distribution:"
kubectl get ingress app-ingress-canary -o jsonpath='{.metadata.annotations.nginx\.ingress\.kubernetes\.io/canary-weight}'
echo ""