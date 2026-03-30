"""Friday Studio — API Tool Wrappers"""

import os, base64, requests

def gpt4o_style_transfer(image_path, prompt):
    """Convert a photo to anime style via GPT-4o."""
    api_key = os.environ.get("OPENAI_API_KEY")
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": prompt}
        ]}], "max_tokens": 4096},
    )
    return response.json()

def neolemon_generate(prompt, reference_image_path=None):
    """Generate Pixar-style image via Neolemon V3 on Segmind."""
    api_key = os.environ.get("SEGMIND_API_KEY")
    payload = {"prompt": prompt, "width": 768, "height": 1024}
    if reference_image_path:
        with open(reference_image_path, "rb") as f:
            payload["reference_image"] = base64.b64encode(f.read()).decode()
    return requests.post("https://api.segmind.com/v1/consistent-character-AI-neolemon-v3",
                         headers={"x-api-key": api_key}, json=payload)

def grok_image_to_video(image_path, prompt, duration=5):
    """Animate a keyframe via Grok Imagine image-to-video."""
    api_key = os.environ.get("GROK_API_KEY")
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    return requests.post("https://api.x.ai/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "grok-2-image", "prompt": prompt, "image": img_b64, "mode": "image-to-video", "duration": duration})

def suno_generate(prompt, instrumental=True):
    """Generate audio via Suno API."""
    api_key = os.environ.get("SUNO_API_KEY")
    return requests.post("https://api.sunoapi.org/v1/generate",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"prompt": prompt, "instrumental": instrumental})
