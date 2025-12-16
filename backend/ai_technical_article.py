import os
from pathlib import Path
from openai import OpenAI


# ---------- CONFIG ----------
IMAGE_DIR = Path("assets/technical_article_images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_TEXT = "gpt-4.1"


def generate_ai_technical_article():
    """
    Generates a modern, trending technical article for a college magazine
    with well-developed paragraphs suitable for print.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set.")

    client = OpenAI(api_key=api_key)

    # ---------- STEP 1: TRENDING TOPIC SELECTION ----------
    topic_prompt = (
        "Select ONE recent and trending computer science topic (2023–2025) "
        "suitable for a college technical magazine.\n\n"
        "Rules:\n"
        "- Must be a current or emerging trend\n"
        "- Avoid generic topics like 'Artificial Intelligence'\n"
        "- Examples (do not copy directly):\n"
        "  • Retrieval-Augmented Generation\n"
        "  • Edge AI\n"
        "  • Digital Twins\n"
        "  • Zero Trust Security\n"
        "  • Multimodal AI Systems\n\n"
        "Return ONLY a short, clear heading (max 8 words)."
    )

    topic_resp = client.responses.create(
        model=MODEL_TEXT,
        input=topic_prompt,
    )

    heading = topic_resp.output_text.strip()

    # ---------- STEP 2: ARTICLE GENERATION ----------
    article_prompt = (
        f"Write a technical article for a college magazine on the topic:\n\n"
        f"'{heading}'\n\n"
        "IMPORTANT RULES:\n"
        "- Do NOT repeat the topic title\n"
        "- Do NOT include headings or subheadings\n"
        "- Do NOT use markdown formatting\n"
        "- Start directly with the introduction paragraph\n\n"
        "CONTENT REQUIREMENTS:\n"
        "- 4 to 6 paragraphs\n"
        "- Each paragraph should be well-developed (80–120 words)\n"
        "- Explain concepts clearly with depth\n"
        "- Discuss why the topic is trending now\n"
        "- Mention real-world applications or systems\n"
        "- Academic but easy-to-understand language\n"
        "- Suitable for undergraduate readers\n"
    )

    article_resp = client.responses.create(
        model=MODEL_TEXT,
        input=article_prompt,
    )

    raw_text = article_resp.output_text.strip()

    paragraphs = []
    for p in raw_text.split("\n"):
        clean = p.strip().replace("**", "")
        if clean and clean.lower() != heading.lower():
            paragraphs.append(clean)

    # ---------- STEP 3: LOCAL IMAGE SELECTION ----------
    images = sorted(str(p) for p in IMAGE_DIR.glob("*.png"))[:1]

    # ---------- FINAL STRUCTURE ----------
    return {
        "text": [heading] + paragraphs,
        "tables": [],
        "images": images,
    }
