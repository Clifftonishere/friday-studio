# Setup Guide

## Prerequisites
- Ubuntu 24.04 server with Docker
- API keys: Anthropic, OpenAI, Segmind, fal.ai

## Deploy
```bash
cp config/.env.example config/.env
nano config/.env  # fill in keys
cd config && docker compose build && docker compose up -d
```

## Verify
```bash
docker ps
docker logs friday-animateme --tail 20
```
