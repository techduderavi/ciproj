#!/bin/bash

# Script to switch between blue and green deployments

# Check current traffic distribution
echo "Current traffic distribution:"
grep -A 2 "upstream backend" nginx.conf

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
    sed -i '' 's/server app-blue:5000 weight=[0-9]*/server app-blue:5000 weight=1/g' nginx.conf
    sed -i '' 's/server app-green:5000 weight=[0-9]*/server app-green:5000 weight=0/g' nginx.conf
    ;;
  2)
    # 100% Green
    sed -i '' 's/server app-blue:5000 weight=[0-9]*/server app-blue:5000 weight=0/g' nginx.conf
    sed -i '' 's/server app-green:5000 weight=[0-9]*/server app-green:5000 weight=1/g' nginx.conf
    ;;
  3)
    # Canary (90% Blue, 10% Green)
    sed -i '' 's/server app-blue:5000 weight=[0-9]*/server app-blue:5000 weight=9/g' nginx.conf
    sed -i '' 's/server app-green:5000 weight=[0-9]*/server app-green:5000 weight=1/g' nginx.conf
    ;;
  4)
    # 50/50 Split
    sed -i '' 's/server app-blue:5000 weight=[0-9]*/server app-blue:5000 weight=1/g' nginx.conf
    sed -i '' 's/server app-green:5000 weight=[0-9]*/server app-green:5000 weight=1/g' nginx.conf
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

# Reload Nginx configuration
docker-compose restart proxy

echo ""
echo "Deployment updated. New traffic distribution:"
grep -A 2 "upstream backend" nginx.conf