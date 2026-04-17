"""Background stage runner.

Dispatches pipeline stages as async tasks, updates the database,
and pushes SSE events to connected clients.
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

from backend.database import (
    get_project, get_stage, update_stage, update_project,
    get_assets, get_uploads, get_soundtrack_config,
    create_asset, STAGE_NAMES, AssetDict,
)


# ---------------------------------------------------------------------------
# SSE event types pushed to the queue
# ---------------------------------------------------------------------------

class StageStartedData(TypedDict):
    stage: int
    name: str


class StageCompleteData(TypedDict):
    stage: int
    asset_count: int


class StageApprovedData(TypedDict):
    stage: int


class ErrorData(TypedDict):
    stage: int
    message: str


class SSEEvent(TypedDict):
    type: str
    data: StageStartedData | StageCompleteData | StageApprovedData | ErrorData

DATA_DIR = os.environ.get("FRIDAY_DATA_DIR", "/data")

# Global event queues: one per active project
event_queues: dict[str, asyncio.Queue[SSEEvent]] = {}


def _project_subdir(project_id: str, subdir: str) -> Path:
    path = Path(f"{DATA_DIR}/projects/{project_id}/{subdir}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_stage(project_id: str, stage_num: int, queue: asyncio.Queue[SSEEvent]) -> None:
    stage = get_stage(project_id, stage_num)
    if not stage:
        return

    update_stage(stage["id"], status="running", started_at=_now())
    await queue.put({
        "type": "stage_started",
        "data": {"stage": stage_num, "name": STAGE_NAMES[stage_num]},
    })

    try:
        result = await asyncio.to_thread(_run_stage_sync, project_id, stage_num, stage["id"])

        update_stage(stage["id"], status="awaiting_review", completed_at=_now())
        await queue.put({
            "type": "stage_complete",
            "data": {"stage": stage_num, "asset_count": len(result)},
        })

    except Exception as e:
        update_stage(stage["id"], status="failed", error_message=str(e), completed_at=_now())
        await queue.put({
            "type": "error",
            "data": {"stage": stage_num, "message": str(e)},
        })


def _run_stage_sync(project_id: str, stage_num: int, stage_id: str) -> list[AssetDict]:
    runners = {
        1: _stage_1_script,
        2: _stage_2_characters,
        3: _stage_3_scenes,
        4: _stage_4_animation,
        5: _stage_5_audio,
        6: _stage_6_assembly,
    }
    runner = runners.get(stage_num)
    if not runner:
        raise ValueError(f"Unknown stage: {stage_num}")
    return runner(project_id, stage_id)


# ---------------------------------------------------------------------------
# Stage implementations
# ---------------------------------------------------------------------------

def _stage_1_script(project_id: str, stage_id: str) -> list[AssetDict]:
    """Script Writer: Generate scene-by-scene breakdown from brief."""
    from crewai import Agent, Task, Crew, Process

    project = get_project(project_id)
    uploads = get_uploads(project_id)
    photo_count = sum(1 for u in uploads if u["media_type"] == "photo")
    video_count = sum(1 for u in uploads if u["media_type"] == "video")
    styles = set(u["style"] for u in uploads)

    agent = Agent(
        role="Script Writer",
        goal="Expand a client brief into a detailed scene-by-scene breakdown",
        backstory="Professional animation scriptwriter. Produces structured scripts with scene numbers, durations, camera directions, emotional beats.",
        llm="anthropic/claude-sonnet-4-5",
        verbose=True, allow_delegation=False,
    )
    task = Task(
        description=(
            f"Create a scene-by-scene script from this brief:\n\n"
            f"{project['brief']}\n\n"
            f"Available media: {photo_count} photos, {video_count} videos\n"
            f"Styles requested: {', '.join(styles)}\n\n"
            f"Output a JSON array of scenes. Each scene should have:\n"
            f"- scene_number (int)\n"
            f"- description (str): what happens in this scene\n"
            f"- duration_seconds (int): 3-8 seconds per scene\n"
            f"- camera (str): camera angle/movement\n"
            f"- emotion (str): emotional tone\n"
            f"- style (str): anime, pixar, or original\n\n"
            f"Aim for 8-15 scenes totaling 60-120 seconds."
        ),
        expected_output="JSON array of scene objects",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()

    asset = create_asset(
        project_id, stage_id, "script",
        text_content=str(result),
    )
    return [asset]


def _stage_2_characters(project_id: str, stage_id: str) -> list[AssetDict]:
    """Character Designer: Generate character sheets from uploaded photos."""
    from pipeline.tools import gpt4o_master_character_sheet, neolemon_generate

    uploads = get_uploads(project_id)
    styled_uploads = [u for u in uploads if u["style"] in ("anime", "pixar") and u["media_type"] == "photo"]
    char_dir = _project_subdir(project_id, "characters")

    assets = []
    for upload in styled_uploads:
        out_filename = f"{upload['id'][:8]}_character_v1.png"
        out_path = str(char_dir / out_filename)

        if upload["style"] == "anime":
            result = gpt4o_master_character_sheet(upload["file_path"])
            _save_openai_image(result, out_path)
        elif upload["style"] == "pixar":
            result = neolemon_generate(
                "Pixar/Disney 3D character sheet. Full body, multiple angles, consistent design.",
                upload["file_path"],
            )
            _save_response_image(result, out_path)

        asset = create_asset(
            project_id, stage_id, "character_sheet",
            file_path=out_path,
            metadata={"upload_id": upload["id"], "style": upload["style"]},
        )
        assets.append(asset)

    return assets


def _stage_3_scenes(project_id: str, stage_id: str) -> list[AssetDict]:
    """Scene Composer: Generate keyframes for each scene."""
    from pipeline.tools import gpt4o_scene_with_ref, neolemon_generate

    scene_dir = _project_subdir(project_id, "scenes")

    script_assets = get_assets(project_id, stage_number=1, asset_type="script", status="approved")
    if not script_assets:
        raise RuntimeError("No approved script found")

    character_assets = get_assets(project_id, stage_number=2, asset_type="character_sheet", status="approved")
    master_ref = character_assets[0]["file_path"] if character_assets else None

    scenes = []
    try:
        scenes = json.loads(script_assets[0]["text_content"])
    except (json.JSONDecodeError, TypeError):
        scenes = [{"scene_number": 1, "description": script_assets[0]["text_content"], "style": "anime"}]

    uploads = get_uploads(project_id)
    assets = []

    for i, scene in enumerate(scenes):
        scene_num = scene.get("scene_number", i + 1)
        description = scene.get("description", "")
        style = scene.get("style", "anime")
        out_filename = f"scene_{scene_num:02d}_v1.png"
        out_path = str(scene_dir / out_filename)

        source_upload = uploads[i % len(uploads)] if uploads else None

        if style == "anime" and master_ref and source_upload:
            result = gpt4o_scene_with_ref(master_ref, source_upload["file_path"], description)
            _save_chat_response_image(result, out_path)
        elif style == "pixar":
            result = neolemon_generate(description, master_ref)
            _save_response_image(result, out_path)

        asset = create_asset(
            project_id, stage_id, "keyframe",
            file_path=out_path,
            metadata={"scene_number": scene_num, "description": description},
        )
        assets.append(asset)

    return assets


def _stage_4_animation(project_id: str, stage_id: str) -> list[AssetDict]:
    """Animator: Convert keyframes to animated clips via Kling on fal.ai."""
    from pipeline.tools import kling_image_to_video, kling_wait_for_video

    clip_dir = _project_subdir(project_id, "clips")

    keyframes = get_assets(project_id, stage_number=3, asset_type="keyframe", status="approved")
    if not keyframes:
        raise RuntimeError("No approved keyframes found")

    assets = []
    for kf in keyframes:
        meta = json.loads(kf["metadata"]) if kf.get("metadata") else {}
        scene_num = meta.get("scene_number", 0)
        description = meta.get("description", "")

        motion_prompt = f"Animate this scene. {description}. Smooth cinematic motion, maintain art style throughout."
        result = kling_image_to_video(kf["file_path"], motion_prompt, duration=5)

        request_id = result.get("request_id")
        if request_id:
            video_result = kling_wait_for_video(request_id)
            video_url = video_result.get("video", {}).get("url", "")
            out_filename = f"clip_{scene_num:02d}_v1.mp4"
            out_path = str(clip_dir / out_filename)
            _download_file(video_url, out_path)
        else:
            out_path = None

        asset = create_asset(
            project_id, stage_id, "clip",
            file_path=out_path,
            metadata={"scene_number": scene_num, "keyframe_id": kf["id"]},
        )
        assets.append(asset)

    return assets


def _stage_5_audio(project_id: str, stage_id: str) -> list[AssetDict]:
    """Audio Producer: Generate soundtrack via MiniMax Music or use uploaded audio."""
    config = get_soundtrack_config(project_id)

    if config and config["mode"] == "upload" and config.get("uploaded_path"):
        asset = create_asset(
            project_id, stage_id, "audio",
            file_path=config["uploaded_path"],
            metadata={"source": "user_upload"},
        )
        return [asset]

    from crewai import Agent, Task, Crew, Process
    from pipeline.tools import music_generate, music_wait_for_result

    project = get_project(project_id)
    script = get_assets(project_id, stage_number=1, asset_type="script", status="approved")
    script_text = script[0]["text_content"] if script else project["brief"]

    agent = Agent(
        role="Audio Producer",
        goal="Generate an instrumental score prompt matching the video emotional arc",
        backstory="Music supervisor. Writes text prompts describing instrumental music — genre, mood, tempo, instruments, and structure.",
        llm="anthropic/claude-sonnet-4-5",
        verbose=True, allow_delegation=False,
    )
    task = Task(
        description=(
            f"Write a music generation prompt for an instrumental soundtrack for this project:\n\n"
            f"Brief: {project['brief']}\n"
            f"Script: {script_text[:500]}\n\n"
            f"The prompt should describe: genre, mood, tempo, instruments, emotional arc, "
            f"and be suitable for a 60-second instrumental track. "
            f"Output ONLY the music prompt text, no explanation."
        ),
        expected_output="Music generation prompt string",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    music_prompt = str(crew.kickoff())

    music_result = music_generate(music_prompt, instrumental=True)

    audio_dir = _project_subdir(project_id, "audio")
    out_path = str(audio_dir / "soundtrack_v1.mp3")

    # fal.ai queue: if we got a request_id, poll for completion
    request_id = music_result.get("request_id")
    if request_id:
        music_result = music_wait_for_result(request_id)

    # Extract audio URL from result
    audio_url = None
    if isinstance(music_result, dict):
        audio = music_result.get("audio") or music_result.get("audio_file") or {}
        if isinstance(audio, dict):
            audio_url = audio.get("url")
        elif isinstance(audio, str):
            audio_url = audio
        if not audio_url:
            audio_url = music_result.get("url")
    if audio_url:
        _download_file(audio_url, out_path)

    asset = create_asset(
        project_id, stage_id, "audio",
        file_path=out_path,
        text_content=music_prompt,
        metadata={"source": "minimax_music"},
    )
    return [asset]


def _stage_6_assembly(project_id: str, stage_id: str) -> list[AssetDict]:
    """Assembly Editor: Stitch all clips + audio into final video."""
    import subprocess

    assembly_dir = _project_subdir(project_id, "assembly")

    clips = get_assets(project_id, stage_number=4, asset_type="clip", status="approved")
    audio_assets = get_assets(project_id, stage_number=5, asset_type="audio", status="approved")

    if not clips:
        raise RuntimeError("No approved clips found")

    clip_paths = [c["file_path"] for c in clips if c.get("file_path")]

    concat_file = str(assembly_dir / "concat.txt")
    with open(concat_file, "w") as f:
        for path in clip_paths:
            f.write(f"file '{path}'\n")

    out_path = str(assembly_dir / "final_v1.mp4")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file]

    if audio_assets and audio_assets[0].get("file_path"):
        audio_path = audio_assets[0]["file_path"]
        cmd += ["-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-shortest"]
    else:
        cmd += ["-c", "copy"]

    cmd.append(out_path)
    subprocess.run(cmd, check=True, capture_output=True)

    asset = create_asset(
        project_id, stage_id, "final_video",
        file_path=out_path,
        metadata={"clip_count": len(clip_paths)},
    )
    return [asset]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_openai_image(api_result: dict[str, Any], out_path: str) -> None:
    import base64
    data = api_result.get("data", [{}])[0]
    if "b64_json" in data:
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(data["b64_json"]))
    elif "url" in data:
        _download_file(data["url"], out_path)


def _save_response_image(response: Any, out_path: str) -> None:
    if hasattr(response, "content"):
        with open(out_path, "wb") as f:
            f.write(response.content)


def _save_chat_response_image(api_result: dict[str, Any], out_path: str) -> None:
    """Extract and download the first URL from a GPT-4o chat vision response."""
    content = api_result["choices"][0]["message"]["content"]
    if "http" in content:
        import re
        urls = re.findall(r'https?://\S+', content)
        if urls:
            _download_file(urls[0], out_path)


def _download_file(url: str, out_path: str) -> None:
    import requests
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(resp.content)
