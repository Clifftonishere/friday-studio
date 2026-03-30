# Setup Guide

## Prerequisites
- Ubuntu 24.04 server with Docker
- Telegram bot token from @BotFather
- API keys: Anthropic, OpenAI, optionally Segmind, xAI/Grok, Suno

## Deploy
```bash
cp config/.env.example config/.env
nano config/.env  # fill in keys
cd config && docker compose up -d
```

## Verify
```bash
docker ps
docker logs friday-animateme --tail 20
```

## Install CrewAI
```bash
./scripts/install-crewai.sh
```
