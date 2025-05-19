#!/bin/bash

# Script to troubleshoot access issues with the application

echo "=== Minikube Status ==="
minikube status

echo ""
echo "=== Minikube IP ==="
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

echo ""
echo "=== /etc/hosts Entry ==="
grep "devops-demo.local" /etc/hosts

echo ""
echo "=== Ingress Addon Status ==="
minikube addons list | grep ingress

echo ""
echo "=== Ingress Controller Pods ==="
kubectl get pods -n ingress-nginx

echo ""
echo "=== Ingress Resources ==="
kubectl get ingress

echo ""
echo "=== Ingress Details ==="
kubectl describe ingress app-ingress
kubectl describe ingress app-ingress-canary

echo ""
echo "=== Services ==="
kubectl get svc

echo ""
echo "=== Endpoints ==="
kubectl get endpoints

echo ""
echo "=== Pods ==="
kubectl get pods

echo ""
echo "=== Testing Connection ==="
echo "Trying to connect to devops-demo.local..."
curl -v http://devops-demo.local

echo ""
echo "=== Troubleshooting Complete ==="
echo "If you're still having issues, try the following:"
echo "1. Restart Minikube: minikube stop && minikube start"
echo "2. Reinstall the Ingress addon: minikube addons disable ingress && minikube addons enable ingress"
echo "3. Use port forwarding as a workaround: kubectl port-forward svc/app-blue-svc 8001:80"