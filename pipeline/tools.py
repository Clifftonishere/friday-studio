"""Friday Studio — API Tool Wrappers

Tool routing:
  - GPT-4o: Image generation only (anime style transfer). Called via OpenAI API.
  - Neolemon V3: Image generation only (Pixar style). Called via Segmind API.
  - Kling AI: Video generation (animate keyframes). Called via fal.ai proxy.
  - MiniMax Music: Audio generation. Called via fal.ai proxy (same FAL_KEY).
  - All agent reasoning runs on Anthropic Claude (configured in pipeline.py).
"""

from __future__ import annotations

import os
import base64
import time
from typing import Any, Callable, TypedDict, TypeVar

import requests
from pathlib import Path


T = TypeVar("T")


# ---------------------------------------------------------------------------
# API response TypedDicts
# ---------------------------------------------------------------------------

class OpenAIImageData(TypedDict, total=False):
    b64_json: str
    url: str


class OpenAIImageResponse(TypedDict):
    data: list[OpenAIImageData]


class ChatMessageContent(TypedDict):
    content: str


class ChatChoice(TypedDict):
    message: ChatMessageContent


class ChatCompletionResponse(TypedDict):
    choices: list[ChatChoice]


class FalQueueSubmitResponse(TypedDict):
    request_id: str
    status_url: str
    response_url: str


class FalQueueStatusResponse(TypedDict, total=False):
    status: str
    logs: list[dict[str, Any]]


class KlingVideoResult(TypedDict, total=False):
    video: dict[str, str]


class MusicAudioFile(TypedDict, total=False):
    url: str


class MusicResult(TypedDict, total=False):
    audio: MusicAudioFile | str
    audio_file: MusicAudioFile
    url: str
    request_id: str

MAX_RETRIES = 3
RETRY_DELAY = 2


def _retry(fn: Callable[[], T], retries: int = MAX_RETRIES) -> T:
    """Retry a function with exponential backoff. Returns result or raises last error."""
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            result = fn()
            return result
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    raise last_err  # type: ignore[misc]


def _load_image_b64(image_path: str) -> str:
    """Load an image file and return base64-encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------------------
# GPT-4o — Anime style transfer (image generation, NOT chat reasoning)
# ---------------------------------------------------------------------------

def gpt4o_master_character_sheet(image_path: str, style_prompt: str | None = None) -> OpenAIImageResponse:
    """Generate a master anime character sheet from a reference photo.

    Uses GPT-4o's image generation with the reference photo as input.
    Returns the API response containing the generated character sheet image.
    """
    from pipeline.prompts import ANIME_MASTER_CHARACTER_SHEET

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    img_b64 = _load_image_b64(image_path)
    prompt = style_prompt or ANIME_MASTER_CHARACTER_SHEET

    def _call():
        resp = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"image": (Path(image_path).name, open(image_path, "rb"), "image/png")},
            data={
                "model": "gpt-image-1",
                "prompt": prompt.strip(),
                "size": "1024x1536",
                "quality": "high",
            },
        )
        resp.raise_for_status()
        return resp.json()

    return _retry(_call)


def gpt4o_scene_with_ref(master_ref_path: str, scene_photo_path: str, scene_description: str) -> ChatCompletionResponse:
    """Generate an anime scene keyframe, maintaining character consistency.

    Two-image input:
      - Image 1 (master_ref_path): The approved master character sheet
      - Image 2 (scene_photo_path): The new scene photo to convert

    Uses the ANIME_SCENE_WITH_REF prompt template to ensure character consistency.
    """
    from pipeline.prompts import ANIME_SCENE_WITH_REF

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    prompt = ANIME_SCENE_WITH_REF.format(scene_description=scene_description).strip()

    def _call():
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{_load_image_b64(master_ref_path)}"},
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{_load_image_b64(scene_photo_path)}"},
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "max_tokens": 4096,
            },
        )
        resp.raise_for_status()
        return resp.json()

    return _retry(_call)


# ---------------------------------------------------------------------------
# Neolemon V3 — Pixar/Disney 3D style (via Segmind API)
# ---------------------------------------------------------------------------

def neolemon_generate(prompt: str, reference_image_path: str | None = None) -> requests.Response:
    """Generate Pixar-style image via Neolemon V3 on Segmind."""
    api_key = os.environ.get("SEGMIND_API_KEY")
    if not api_key:
        raise ValueError("SEGMIND_API_KEY not set")

    payload = {"prompt": prompt, "width": 768, "height": 1024}
    if reference_image_path:
        payload["reference_image"] = _load_image_b64(reference_image_path)

    def _call():
        resp = requests.post(
            "https://api.segmind.com/v1/consistent-character-AI-neolemon-v3",
            headers={"x-api-key": api_key},
            json=payload,
        )
        resp.raise_for_status()
        return resp

    return _retry(_call)


# ---------------------------------------------------------------------------
# Kling AI — Image-to-video animation via fal.ai proxy (primary provider)
# ---------------------------------------------------------------------------

FAL_KLING_MODEL = "fal-ai/kling-video/v2.6/pro/image-to-video"
FAL_QUEUE_URL = "https://queue.fal.run"


def _fal_headers() -> dict[str, str]:
    """Get fal.ai auth headers."""
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        raise ValueError("FAL_KEY not set")
    return {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
    }


def _fal_queue_poll(model: str, request_id: str) -> FalQueueStatusResponse:
    """Poll fal.ai queue for job status."""
    resp = requests.get(
        f"{FAL_QUEUE_URL}/{model}/requests/{request_id}/status",
        headers=_fal_headers(),
        params={"logs": "1"},
    )
    resp.raise_for_status()
    return resp.json()


def _fal_queue_get_result(model: str, request_id: str) -> dict[str, Any]:
    """Fetch the completed result from the fal.ai queue."""
    resp = requests.get(
        f"{FAL_QUEUE_URL}/{model}/requests/{request_id}",
        headers=_fal_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def _fal_queue_wait(model: str, request_id: str, poll_interval: int, timeout: int, label: str) -> dict[str, Any]:
    """Wait for a fal.ai queue job to complete.

    Polls _fal_queue_poll until the status is COMPLETED, then fetches and
    returns the result. Raises on FAILED status or timeout.
    """
    start = time.time()
    while time.time() - start < timeout:
        status = _fal_queue_poll(model, request_id)
        if status.get("status") == "COMPLETED":
            return _fal_queue_get_result(model, request_id)
        if status.get("status") == "FAILED":
            raise RuntimeError(f"{label} failed: {status}")
        time.sleep(poll_interval)
    raise TimeoutError(f"{label} timed out after {timeout}s")


def kling_image_to_video(image_path: str, prompt: str, duration: int = 5, negative_prompt: str = "blur, distort, low quality") -> FalQueueSubmitResponse:
    """Animate a keyframe via Kling 2.6 Pro on fal.ai.

    Submits to fal.ai's queue and returns the request_id for polling.

    Args:
        image_path: Path to the styled keyframe image
        prompt: Motion description prompt
        duration: 5 or 10 seconds
        negative_prompt: What to avoid in generation

    Returns:
        dict with request_id, status_url, response_url
    """
    img_b64 = _load_image_b64(image_path)
    image_uri = f"data:image/png;base64,{img_b64}"

    def _call():
        resp = requests.post(
            f"{FAL_QUEUE_URL}/{FAL_KLING_MODEL}",
            headers=_fal_headers(),
            json={
                "prompt": prompt,
                "start_image_url": image_uri,
                "duration": str(duration),
                "negative_prompt": negative_prompt,
            },
        )
        resp.raise_for_status()
        return resp.json()

    return _retry(_call)


def kling_wait_for_video(request_id: str, poll_interval: int = 5, timeout: int = 900) -> dict[str, Any]:
    """Wait for Kling video generation to complete on fal.ai.

    Kling takes 5-14 minutes typically, so timeout defaults to 15 min.

    Returns:
        dict with video URL on success, raises on failure/timeout
    """
    return _fal_queue_wait(
        FAL_KLING_MODEL, request_id, poll_interval, timeout,
        "Kling video generation",
    )


# ---------------------------------------------------------------------------
# MiniMax Music — Audio score generation via fal.ai
# ---------------------------------------------------------------------------

FAL_MINIMAX_MODEL = "fal-ai/minimax-music"


def music_generate(prompt: str, instrumental: bool = True) -> FalQueueSubmitResponse:
    """Generate audio via MiniMax Music on fal.ai.

    Uses the same FAL_KEY as Kling video generation.

    Args:
        prompt: Text description of the music (genre, mood, tempo, structure)
        instrumental: If True, generates instrumental only (no vocals)

    Returns:
        dict with request_id for polling, or completed result
    """
    if instrumental and "instrumental" not in prompt.lower():
        prompt = f"[Instrumental] {prompt}"

    def _call():
        resp = requests.post(
            f"{FAL_QUEUE_URL}/{FAL_MINIMAX_MODEL}",
            headers=_fal_headers(),
            json={
                "prompt": prompt,
            },
        )
        resp.raise_for_status()
        return resp.json()

    return _retry(_call)


def music_wait_for_result(request_id: str, poll_interval: int = 5, timeout: int = 300) -> dict[str, Any]:
    """Wait for music generation to complete on fal.ai.

    Returns:
        dict with audio URL on success, raises on failure/timeout
    """
    return _fal_queue_wait(
        FAL_MINIMAX_MODEL, request_id, poll_interval, timeout,
        "Music generation",
    )
