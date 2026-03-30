"""Friday Studio — Prompt Templates"""

ANIME_MASTER_CHARACTER_SHEET = """
Convert this photo into anime style in the exact style of Hajime no Ippo
and Megalo Box. Full cel-shaded animation art with bold black outlines,
flat color fills, dramatic shading with hard shadow edges. Keep the exact
same pose, composition, and clothing. No photorealism. 9:16 vertical.
"""

ANIME_SCENE_WITH_REF = """
Image 1 is the definitive anime character design for this subject.
Image 2 is the new scene to convert.

Convert Image 2 into anime style, matching the EXACT character design
from Image 1. Only pose, clothing, and environment change.
Style: Hajime no Ippo / Megalo Box. Cel-shaded, bold outlines. 9:16.

Scene details: {scene_description}
"""

GROK_ANIME_MOTION = """
Animate this anime {subject_type}. {motion_description}.
Keep the cel-shaded anime style throughout. {camera_direction}. {duration}s.
"""

SUNO_BOXING_PROMO = """
[Instrumental] Dark trap beat with orchestral strings. Atmospheric intro
with crowd noise. Hard 808s and brass at 0:40. Orchestral climax at 1:20.
Piano and strings resolution. 2 minutes. No vocals. Cinematic boxing energy.
"""
