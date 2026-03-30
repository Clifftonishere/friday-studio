# Friday Studio

AI-powered animated video production pipeline. Creates Pixar-style and anime-style animated videos from raw photos and video clips.

Friday is a Telegram bot backed by [OpenClaw](https://github.com/openclaw/openclaw) and [CrewAI](https://github.com/crewAIInc/crewAI), running as a Docker container on a Hetzner VPS.

## Architecture
```
User (Telegram) → Friday Bot → CrewAI Pipeline → Generated Video

Style Selection
      │
      ├── Pixar/Disney 3D ──→ Neolemon V3 (Segmind API)
      │
      └── Anime ──→ GPT-4o (style transfer) → Grok Imagine (animation)
      │
      ↓ Both branches converge
      │
      ├── Grok Imagine (clip animation)
      ├── Suno V5 (audio score)
      └── FFmpeg → VectCutAPI → CapCut (assembly)
```

### Two-Stage Anime Pipeline (Validated)

1. **GPT-4o** converts raw photos into anime-style keyframes (cel-shaded, bold outlines, flat colors)
2. **Grok Imagine** takes the anime keyframes and animates them (motion, speed lines, effects)

This produces dramatically better results than single-pass approaches.

## Pipeline Stages

Each stage requires explicit user approval before proceeding:

| Stage | Agent | Tool (Pixar) | Tool (Anime) |
|-------|-------|-------------|--------------|
| 1. Storyline | Script Writer | Claude | Claude |
| 2. Character Design | Character Designer | Neolemon V3 | GPT-4o |
| 3. Scene Frames | Scene Composer | Neolemon V3 | GPT-4o |
| 4. Animated Clips | Animator | Grok Imagine | Grok Imagine |
| 5. Audio Score | Audio Producer | Suno V5 | Suno V5 |
| 6. Final Assembly | Assembly Editor | FFmpeg + VectCutAPI | FFmpeg + VectCutAPI |

## Cost Per Project

- **Anime branch**: ~$2–5 per video
- **Pixar branch**: ~$2–4 per video

## Quick Start
```bash
git clone https://github.com/Clifftonishere/friday-studio.git
cd friday-studio
cp config/.env.example config/.env
# Edit config/.env with your API keys
./scripts/deploy.sh
```

## Project Structure
```
friday-studio/
├── config/           # Docker + env config
├── pipeline/         # CrewAI agents and API wrappers
├── docs/             # Architecture, setup, testing logs
├── examples/         # Example projects
├── scripts/          # Deploy and install scripts
└── workspace/        # Friday bot personality
```

## What Was Tested and Eliminated

| Tool | Result | Reason |
|------|--------|--------|
| fal.ai IP-Adapter | ❌ | Photorealistic output, not genuine anime |
| fal.ai SDXL + LoRA | ❌ | Lost character entirely |
| AniFun.ai | ❌ | Unacceptable quality |
| Kling 3.0 | ❌ | Quality not up to par |
| Grok (text-to-video) | ❌ | All failure modes |
| Grok (i2v with real photo) | ⚠️ | Uncanny middle ground |
| **GPT-4o → Grok (i2v)** | **✅** | **Best quality, validated** |

## Author

**Cliffton Lee** ([@Clifftonishere](https://github.com/Clifftonishere))
