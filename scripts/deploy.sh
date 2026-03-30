#!/bin/bash
set -e
echo "Deploying Friday Studio..."
if [ ! -f config/.env ]; then
    echo "config/.env not found. Copy config/.env.example first."
    exit 1
fi
cd config && docker compose up -d
sleep 5
docker ps | grep friday-animateme && echo "Friday is running." || echo "Failed. Check: docker logs friday-animateme"
