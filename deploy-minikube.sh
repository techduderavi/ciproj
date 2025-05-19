#!/bin/bash

# Script to deploy the application to Minikube

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
  echo "Starting Minikube..."
  minikube start
fi

# Enable the Ingress addon if not already enabled
if ! minikube addons list | grep -q "ingress: enabled"; then
  echo "Enabling Ingress addon..."
  minikube addons enable ingress
fi

# Set up Docker to use Minikube's Docker daemon
echo "Configuring Docker to use Minikube's Docker daemon..."
eval $(minikube docker-env)

# Build the Docker image inside Minikube
echo "Building Docker image in Minikube..."
docker build -t devops-demo:latest .

# Create a directory for the database if it doesn't exist
minikube ssh "mkdir -p /data"

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/blue-deployment.yaml
kubectl apply -f k8s/green-deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/app-blue
kubectl wait --for=condition=available --timeout=300s deployment/app-green

# Add host entry to /etc/hosts if not already present
if ! grep -q "devops-demo.local" /etc/hosts; then
  echo "Adding devops-demo.local to /etc/hosts..."
  echo "$(minikube ip) devops-demo.local" | sudo tee -a /etc/hosts
fi

echo "Deployment complete!"
echo "Access the application at http://devops-demo.local"
