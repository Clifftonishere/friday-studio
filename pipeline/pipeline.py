"""
Friday Studio — AnimateMe Production Pipeline
Six-agent CrewAI pipeline for animated video production.

Style routing:
  - Anime: GPT-4o (character/scene) → Grok Imagine (animation)
  - Pixar: Neolemon V3 via Segmind (character/scene) → Grok Imagine (animation)
"""

import os
from crewai import Agent, Task, Crew, Process

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SEGMIND_API_KEY = os.environ.get("SEGMIND_API_KEY")
GROK_API_KEY = os.environ.get("GROK_API_KEY")
SUNO_API_KEY = os.environ.get("SUNO_API_KEY")

ORCHESTRATION_LLM = "anthropic/claude-sonnet-4-5"

script_writer = Agent(
    role="Script Writer",
    goal="Expand a client brief into a detailed scene-by-scene breakdown",
    backstory="Professional animation scriptwriter. Produces structured scripts with scene numbers, durations, camera directions, emotional beats.",
    llm=ORCHESTRATION_LLM,
    verbose=True, allow_delegation=False,
)

character_designer = Agent(
    role="Character Designer",
    goal="Generate character reference images from uploaded photos",
    backstory="Animation character designer. For ANIME: writes GPT-4o prompts for cel-shaded style transfer. For PIXAR: writes Neolemon V3 prompts with reference anchoring. Always creates a MASTER CHARACTER SHEET first for consistency.",
    llm=ORCHESTRATION_LLM,
    verbose=True, allow_delegation=False,
)

scene_composer = Agent(
    role="Scene Composer",
    goal="Generate each scene as a static keyframe using approved character references",
    backstory="Animation scene composer. Every prompt references the master character sheet to maintain consistency. Specifies camera angle, lighting, positioning, and emotional tone.",
    llm=ORCHESTRATION_LLM,
    verbose=True, allow_delegation=False,
)

animator = Agent(
    role="Animator",
    goal="Convert static keyframes into animated clips via Grok Imagine",
    backstory="Animation director. Writes motion-only prompts for Grok image-to-video. Never re-describes the image — only describes what should MOVE.",
    llm=ORCHESTRATION_LLM,
    verbose=True, allow_delegation=False,
)

audio_producer = Agent(
    role="Audio Producer",
    goal="Generate an instrumental score matching the video emotional arc",
    backstory="Music supervisor. Writes Suno V5 prompts with structure tags matching the video pacing.",
    llm=ORCHESTRATION_LLM,
    verbose=True, allow_delegation=False,
)

assembly_editor = Agent(
    role="Assembly Editor",
    goal="Sequence all clips with transitions and audio into a final video",
    backstory="Post-production editor. Produces FFmpeg commands and VectCutAPI drafts for CapCut final polish.",
    llm=ORCHESTRATION_LLM,
    verbose=True, allow_delegation=False,
)


def run_pipeline(brief, style="anime", photos=None, videos=None):
    script_task = Task(
        description=f"Create scene-by-scene script from: {brief}\nStyle: {style}\nPhotos: {len(photos or [])}\nVideos: {len(videos or [])}",
        expected_output="Structured scene-by-scene script with 8-15 scenes",
        agent=script_writer,
    )
    character_task = Task(
        description=f"Generate character design prompts for style: {style}. Create MASTER CHARACTER SHEET first.",
        expected_output="Master character sheet prompt + individual character prompts",
        agent=character_designer,
    )
    scene_task = Task(
        description=f"Generate keyframe prompts for every scene using approved character refs. Style: {style}",
        expected_output="One detailed keyframe prompt per scene",
        agent=scene_composer,
    )
    animation_task = Task(
        description="Write Grok Imagine image-to-video prompts. Motion only — not image content.",
        expected_output="One animation prompt per scene with duration",
        agent=animator,
    )
    audio_task = Task(
        description="Write Suno V5 prompt for instrumental score with structure tags.",
        expected_output="Complete Suno V5 prompt",
        agent=audio_producer,
    )
    assembly_task = Task(
        description="Produce FFmpeg assembly commands and VectCutAPI draft generation.",
        expected_output="FFmpeg + VectCutAPI commands",
        agent=assembly_editor,
    )

    crew = Crew(
        agents=[script_writer, character_designer, scene_composer, animator, audio_producer, assembly_editor],
        tasks=[script_task, character_task, scene_task, animation_task, audio_task, assembly_task],
        process=Process.sequential, verbose=True,
    )
    return crew.kickoff()


if __name__ == "__main__":
    result = run_pipeline(
        brief="A 2-minute boxing promo for a Singapore-based professional boxer. Interleave real footage with anime sequences.",
        style="anime",
        photos=["photo1.jpg", "photo2.jpg"],
        videos=["clip1.mov", "clip2.mov"],
    )
    print(result)
