"""Gemini API tools for image generation and editing."""

import os
import time
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

from .utils import (
    get_mime_type,
    get_output_path,
    logger,
    validate_aspect_ratio,
    validate_model,
    validate_resolution,
)

# Maximum retries for API calls
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def get_client() -> genai.Client:
    """Get Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)


def _retry_api_call(func, *args, **kwargs):
    """Execute an API call with retry logic."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            logger.warning(f"API call failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
    raise last_error


async def generate_image(
    prompt: str,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_path: str | None = None,
) -> str:
    """
    Generate an image from a text prompt using Gemini.

    Args:
        prompt: Text description of the image to generate
        model: Gemini model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview)
        aspect_ratio: Image aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
        resolution: Image resolution (1K, 2K, 4K)
        output_path: Optional custom output path for the generated image

    Returns:
        Path to the generated image and any accompanying text from the model
    """
    model = validate_model(model)
    aspect_ratio = validate_aspect_ratio(aspect_ratio)
    resolution = validate_resolution(resolution)

    client = get_client()

    logger.info(f"Generating image with model={model}, aspect_ratio={aspect_ratio}, resolution={resolution}")

    # Note: image_size is not supported on AI Studio, only aspect_ratio
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
        ),
    )

    response = _retry_api_call(
        client.models.generate_content,
        model=model,
        contents=[prompt],
        config=config,
    )

    result_text = ""
    image_saved = False
    final_path = None

    for part in response.parts:
        if part.text:
            result_text = part.text
        elif part.inline_data:
            final_path = get_output_path(prompt, output_path)
            image = part.as_image()
            image.save(str(final_path))
            image_saved = True
            logger.info(f"Image saved to {final_path}")

    if not image_saved:
        return f"No image was generated. Model response: {result_text or 'No response'}"

    result = f"Image saved to: {final_path}"
    if result_text:
        result += f"\n\nModel notes: {result_text}"

    return result


async def edit_image(
    image_path: str,
    prompt: str,
    model: str = "gemini-2.5-flash-image",
    output_path: str | None = None,
) -> str:
    """
    Edit an existing image based on text instructions using Gemini.

    Args:
        image_path: Path to the image to edit
        prompt: Text instructions for how to edit the image
        model: Gemini model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview)
        output_path: Optional custom output path for the edited image

    Returns:
        Path to the edited image and any accompanying text from the model
    """
    model = validate_model(model)

    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    client = get_client()

    logger.info(f"Editing image {image_path} with model={model}")

    # Load the image
    image = Image.open(image_path)

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
    )

    response = _retry_api_call(
        client.models.generate_content,
        model=model,
        contents=[prompt, image],
        config=config,
    )

    result_text = ""
    image_saved = False
    final_path = None

    for part in response.parts:
        if part.text:
            result_text = part.text
        elif part.inline_data:
            final_path = get_output_path(f"edited_{prompt}", output_path)
            edited_image = part.as_image()
            edited_image.save(str(final_path))
            image_saved = True
            logger.info(f"Edited image saved to {final_path}")

    if not image_saved:
        return f"No edited image was generated. Model response: {result_text or 'No response'}"

    result = f"Edited image saved to: {final_path}"
    if result_text:
        result += f"\n\nModel notes: {result_text}"

    return result


async def generate_with_references(
    prompt: str,
    reference_images: list[str],
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_path: str | None = None,
) -> str:
    """
    Generate an image using reference images for style or content guidance.

    Args:
        prompt: Text description of the image to generate
        reference_images: List of paths to reference images (max 14 for gemini-3-pro, max 3 for gemini-2.5-flash)
        model: Gemini model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview)
        aspect_ratio: Image aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
        resolution: Image resolution (1K, 2K, 4K)
        output_path: Optional custom output path for the generated image

    Returns:
        Path to the generated image and any accompanying text from the model
    """
    model = validate_model(model)
    aspect_ratio = validate_aspect_ratio(aspect_ratio)
    resolution = validate_resolution(resolution)

    # Validate reference images limit
    max_refs = 14 if "3-pro" in model else 3
    if len(reference_images) > max_refs:
        return f"Error: Maximum {max_refs} reference images allowed for {model}"

    # Verify all reference images exist
    missing = [p for p in reference_images if not Path(p).exists()]
    if missing:
        return f"Error: Reference images not found: {missing}"

    client = get_client()

    logger.info(f"Generating with {len(reference_images)} references, model={model}")

    # Build content with prompt and images
    content = [prompt]
    for ref_path in reference_images:
        content.append(Image.open(ref_path))

    # Note: image_size is not supported on AI Studio, only aspect_ratio
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
        ),
    )

    response = _retry_api_call(
        client.models.generate_content,
        model=model,
        contents=content,
        config=config,
    )

    result_text = ""
    image_saved = False
    final_path = None

    for part in response.parts:
        if part.text:
            result_text = part.text
        elif part.inline_data:
            final_path = get_output_path(prompt, output_path)
            image = part.as_image()
            image.save(str(final_path))
            image_saved = True
            logger.info(f"Image saved to {final_path}")

    if not image_saved:
        return f"No image was generated. Model response: {result_text or 'No response'}"

    result = f"Image saved to: {final_path}"
    if result_text:
        result += f"\n\nModel notes: {result_text}"

    return result


async def describe_image(
    image_path: str,
    detail_level: str = "detailed",
) -> str:
    """
    Get a description of an image using Gemini.

    Args:
        image_path: Path to the image to describe
        detail_level: Level of detail (brief, detailed, technical)

    Returns:
        Text description of the image
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    client = get_client()

    # Build prompt based on detail level
    prompts = {
        "brief": "Describe this image in one or two sentences.",
        "detailed": "Provide a detailed description of this image, including the main subjects, colors, composition, and mood.",
        "technical": "Provide a technical analysis of this image, including composition, lighting, color palette, style, and any text visible. Also note the apparent resolution and image quality.",
    }
    prompt = prompts.get(detail_level, prompts["detailed"])

    logger.info(f"Describing image {image_path} with detail_level={detail_level}")

    image = Image.open(image_path)

    response = _retry_api_call(
        client.models.generate_content,
        model="gemini-2.5-flash-image",
        contents=[prompt, image],
    )

    return response.text or "Could not generate description"
