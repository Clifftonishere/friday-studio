# Architecture

## Decision Tree
```
User selects style
    ├── Pixar/Disney 3D
    │     ├── Character Design → Neolemon V3 (Segmind API)
    │     └── Scene Generation → Neolemon V3
    └── Anime
          ├── Character Design → GPT-4o (OpenAI API)
          └── Scene Generation → GPT-4o
    ↓ Converge
    ├── Animation → Kling 2.6 Pro via fal.ai (image-to-video)
    ├── Audio → MiniMax Music via fal.ai
    └── Assembly → FFmpeg
```

## Cost Per Project

| Step | Anime Cost | Pixar Cost |
|------|-----------|------------|
| Character refs | ~$0.20-0.30 | ~$0.15-0.20 |
| Scene generation | ~$0.50-1.00 | ~$0.35-0.75 |
| Animation (Kling) | ~$0.35-0.70 | ~$0.35-0.70 |
| Audio (MiniMax) | ~$0.04 | ~$0.04 |
| Assembly | Free | Free |
| **Total** | **~$1.09-2.04** | **~$0.89-1.69** |
