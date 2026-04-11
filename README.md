# Friday Studio

AI-powered animated video production pipeline. Creates Pixar-style and anime-style animated videos from raw photos and video clips.

Web interface backed by FastAPI + Next.js, with a CrewAI pipeline running on Claude Sonnet 4.5. Deployed as a Docker container on a Hetzner VPS.

## Architecture
```
User (Web UI) → FastAPI Backend → CrewAI Pipeline → Generated Video

Style Selection
      │
      ├── Pixar/Disney 3D ──→ Neolemon V3 (Segmind API)
      │
      └── Anime ──→ GPT-4o (style transfer) → Kling 2.6 Pro (animation)
      │
      ↓ Both branches converge
      │
      ├── Kling 2.6 Pro via fal.ai (clip animation)
      ├── MiniMax Music via fal.ai (audio score)
      └── FFmpeg (assembly)
```

### Two-Stage Anime Pipeline (Validated)

1. **GPT-4o** converts raw photos into anime-style keyframes (cel-shaded, bold outlines, flat colors)
2. **Kling 2.6 Pro** takes the anime keyframes and animates them (motion, speed lines, effects)

This produces dramatically better results than single-pass approaches.

## Pipeline Stages

Each stage requires explicit user approval before proceeding:

| Stage | Agent | Tool (Pixar) | Tool (Anime) |
|-------|-------|-------------|--------------|
| 1. Storyline | Script Writer | Claude | Claude |
| 2. Character Design | Character Designer | Neolemon V3 | GPT-4o |
| 3. Scene Frames | Scene Composer | Neolemon V3 | GPT-4o |
| 4. Animated Clips | Animator | Kling 2.6 Pro | Kling 2.6 Pro |
| 5. Audio Score | Audio Producer | MiniMax Music | MiniMax Music |
| 6. Final Assembly | Assembly Editor | FFmpeg | FFmpeg |

## Cost Per Project

- **Anime branch**: ~$2-5 per video
- **Pixar branch**: ~$2-4 per video

## Quick Start
```bash
git clone https://github.com/Clifftonishere/friday-studio.git
cd friday-studio
cp config/.env.example config/.env
# Edit config/.env with your API keys
cd config
docker compose build && docker compose up -d
# Access at http://localhost:8000
```

## Project Structure
```
friday-studio/
├── backend/          # FastAPI app, SQLite, routes, worker
├── frontend/         # Next.js (static export)
├── pipeline/         # CrewAI agents, API wrappers, prompts
├── config/           # Dockerfile, docker-compose, .env
├── docs/             # Architecture, setup, testing logs
├── examples/         # Example projects
├── scripts/          # Deploy and install scripts
└── workspace/        # Friday bot personality
```

## API Keys Required

| Key | Service | Used For |
|-----|---------|----------|
| `ANTHROPIC_API_KEY` | Anthropic | Agent reasoning (Claude Sonnet 4.5) |
| `OPENAI_API_KEY` | OpenAI | GPT-4o anime style transfer |
| `SEGMIND_API_KEY` | Segmind | Neolemon V3 Pixar generation |
| `FAL_KEY` | fal.ai | Kling video + MiniMax Music audio |
| `GROK_API_KEY` | xAI | Grok Imagine (fallback video) |

## What Was Tested and Eliminated

| Tool | Result | Reason |
|------|--------|--------|
| fal.ai IP-Adapter | :x: | Photorealistic output, not genuine anime |
| fal.ai SDXL + LoRA | :x: | Lost character entirely |
| AniFun.ai | :x: | Unacceptable quality |
| Kling 3.0 (direct) | :x: | Quality not up to par with raw photo input |
| Grok (text-to-video) | :x: | All failure modes |
| Grok (i2v with real photo) | :warning: | Uncanny middle ground |
| Stability AI SVD | :x: | API sunset July 2025, max 2s output |
| **GPT-4o keyframe + Kling i2v** | :white_check_mark: | **Best quality, validated** |

## Author

**Cliffton Lee** ([@Clifftonishere](https://github.com/Clifftonishere))
