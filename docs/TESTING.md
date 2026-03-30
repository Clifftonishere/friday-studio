# Testing Log

## Key Finding
Single-pass style transfer + animation fails. Two-stage works:
1. GPT-4o converts photo → anime keyframe
2. Grok Imagine animates the keyframe

## Results
| Tool | Test | Result |
|------|------|--------|
| fal.ai IP-Adapter Face ID | Photo → anime | ❌ Photorealistic filter |
| fal.ai SDXL + Anime LoRA | Scene gen | ❌ Lost character |
| AniFun.ai | Photo → anime | ❌ Bad quality |
| Kling 3.0 | Image → video | ❌ Not up to par |
| Grok (text-to-video) | Text → anime video | ❌ All failure modes |
| Grok (i2v with real photo) | Photo → anime video | ⚠️ Uncanny middle ground |
| **GPT-4o keyframe → Grok i2v** | **Two-stage** | **✅ PsyopAnime quality** |
