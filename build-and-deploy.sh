#!/bin/bash

# Script to build the Docker image in Minikube and deploy the application

# Set up Docker to use Minikube's Docker daemon
echo "Configuring Docker to use Minikube's Docker daemon..."
eval $(minikube docker-env)

# Build the Docker image inside Minikube
echo "Building Docker image in Minikube..."
docker build -t devops-demo:latest .

# Delete existing deployments if they exist
echo "Deleting existing deployments..."
kubectl delete deployment app-blue app-green --ignore-not-found

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

echo "Deployment complete!"
echo "Access the application at http://devops-demo.local"