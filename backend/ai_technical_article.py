import os
from pathlib import Path
from openai import OpenAI
from backend.image_generator_hf import generate_image_for_topic


# ---------- CONFIG ----------
IMAGE_DIR = Path("assets/technical_article_images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_TEXT = "gpt-4.1"


def generate_ai_technical_article():
    """
    Generates a modern, trending technical article for a college magazine.
    Topic + text from OpenAI, image from Hugging Face.
    """

    # ---------- OPENAI SETUP ----------
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
        "- Heading must be short (max 8 words)\n"
        "- Clear and specific\n\n"
        "Return ONLY the heading."
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
        "- Do NOT use markdown\n"
        "- Start directly with the introduction paragraph\n\n"
        "CONTENT REQUIREMENTS:\n"
        "- 4 to 6 paragraphs\n"
        "- Each paragraph must be 90–130 words\n"
        "- Explain concepts clearly and deeply\n"
        "- Explain why the topic is trending now\n"
        "- Mention real-world applications\n"
        "- Academic but easy-to-understand tone\n"
        "- Suitable for undergraduate readers\n"
    )

    article_resp = client.responses.create(
        model=MODEL_TEXT,
        input=article_prompt,
    )

    raw_text = article_resp.output_text.strip()

    paragraphs = []
    for p in raw_text.split("\n"):
        clean = p.strip()
        if clean and clean.lower() != heading.lower():
            paragraphs.append(clean)

    # ---------- STEP 3: IMAGE GENERATION (HUGGING FACE) ----------
    image_path = generate_image_for_topic(heading)
    images = [image_path]

    # ---------- FINAL STRUCTURE ----------
    return {
        "text": [heading] + paragraphs,
        "tables": [],
        "images": images,
    }
