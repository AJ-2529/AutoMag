# backend/image_generator_hf.py

import os
import requests
from pathlib import Path

HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

IMAGE_DIR = Path("assets/technical_article_images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def generate_image_for_topic(topic: str) -> str:
    """
    Generates ONE academic-style image for a technical topic
    using Hugging Face Stable Diffusion XL.
    """

    hf_key = os.getenv("HF_API_KEY")
    if not hf_key:
        raise RuntimeError("HF_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json",
    }

    prompt = (
        f"Minimalist conceptual illustration representing the idea of {topic}. "
    "Clean and modern visual style, smooth shapes, soft lighting, "
    "abstract technological theme, professional academic look. "
    "Simple composition, neutral colors, white or light background. "
    "No text, no labels, no diagrams, no arrows, no people, no watermark."
    )

    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": prompt},
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Hugging Face image generation failed: {response.text}"
        )

    img_path = IMAGE_DIR / "technical_article.png"

    with open(img_path, "wb") as f:
        f.write(response.content)

    return str(img_path)
