#!/bin/bash

# Script to set up proper access to the application in Minikube

# Enable ingress if not already enabled
if ! minikube addons list | grep -q "ingress: enabled"; then
  echo "Enabling Ingress addon..."
  minikube addons enable ingress
  
  # Wait for ingress controller to be ready
  echo "Waiting for Ingress controller to be ready..."
  kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=120s
fi

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Update /etc/hosts file
if grep -q "devops-demo.local" /etc/hosts; then
  echo "Updating devops-demo.local entry in /etc/hosts..."
  sudo sed -i '' "s/.*devops-demo.local/$MINIKUBE_IP devops-demo.local/" /etc/hosts
else
  echo "Adding devops-demo.local to /etc/hosts..."
  echo "$MINIKUBE_IP devops-demo.local" | sudo tee -a /etc/hosts
fi

# Apply or update the services and ingress
echo "Applying service and ingress configurations..."
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Wait for ingress to be ready
echo "Waiting for Ingress to be ready..."
kubectl wait --for=condition=ready ingress/app-ingress --timeout=60s

echo "Setup complete!"
echo "You should now be able to access the application at http://devops-demo.local"
echo ""
echo "If you still have issues, you can use port forwarding:"
echo "kubectl port-forward svc/app-blue-svc 8001:80"
echo "kubectl port-forward svc/app-green-svc 8002:80"
echo ""
echo "Then access the application at http://localhost:8001 or http://localhost:8002"