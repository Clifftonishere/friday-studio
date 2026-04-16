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

