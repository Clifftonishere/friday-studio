# Testing Log

## Key Finding
Single-pass style transfer + animation fails. Two-stage works:
1. GPT-4o converts photo to anime keyframe
2. Kling 2.6 Pro animates the keyframe (via fal.ai)

## Results
| Tool | Test | Result |
|------|------|--------|
| fal.ai IP-Adapter Face ID | Photo to anime | Failed: Photorealistic filter |
| fal.ai SDXL + Anime LoRA | Scene gen | Failed: Lost character |
| AniFun.ai | Photo to anime | Failed: Bad quality |
| Kling 3.0 (direct, raw photo) | Image to video | Failed: Not up to par |
| Grok (text-to-video) | Text to anime video | Failed: All failure modes |
| Grok (i2v with real photo) | Photo to anime video | Partial: Uncanny middle ground |
| Stability AI SVD | Image to video | Failed: API sunset July 2025, max 2s |
| **GPT-4o keyframe + Kling 2.6 Pro i2v** | **Two-stage** | **Validated** |
