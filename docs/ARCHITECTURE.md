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
    ├── Animation → Grok Imagine (image-to-video)
    ├── Audio → Suno V5
    └── Assembly → FFmpeg → VectCutAPI → CapCut
```

## Cost Per Project

| Step | Anime Cost | Pixar Cost |
|------|-----------|------------|
| Character refs | ~$0.20-0.30 | ~$0.15-0.20 |
| Scene generation | ~$0.50-1.00 | ~$0.35-0.75 |
| Animation | ~$1.50-2.25 | ~$1.50-2.25 |
| Audio | ~$0.10 | ~$0.10 |
| Assembly | Free | Free |
| **Total** | **~$2.30-3.65** | **~$2.10-3.30** |
