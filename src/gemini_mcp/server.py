"""Gemini MCP Server - Main entry point."""

from mcp.server.fastmcp import FastMCP

from .gemini_tools import (
    describe_image,
    edit_image,
    generate_image,
    generate_with_references,
)
from .imagemagick_tools import (
    add_border,
    apply_effects,
    composite_images,
    convert_format,
    create_thumbnail,
    crop_image,
    flip_image,
    get_image_info,
    resize_image,
    rotate_image,
)

# Initialize FastMCP server
mcp = FastMCP("gemini-image")


# ============================================================================
# Gemini AI Tools
# ============================================================================


@mcp.tool()
async def gemini_generate_image(
    prompt: str,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_path: str | None = None,
) -> str:
    """
    Generate an image from a text prompt using Gemini AI.

    Args:
        prompt: Text description of the image to generate
        model: Gemini model (gemini-2.5-flash-image for speed, gemini-3-pro-image-preview for quality)
        aspect_ratio: Image aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
        resolution: Image resolution (1K, 2K, 4K - higher = better quality but slower)
        output_path: Optional custom output path for the generated image

    Returns:
        Path to the generated image
    """
    return await generate_image(prompt, model, aspect_ratio, resolution, output_path)


@mcp.tool()
async def gemini_edit_image(
    image_path: str,
    prompt: str,
    model: str = "gemini-2.5-flash-image",
    output_path: str | None = None,
) -> str:
    """
    Edit an existing image using Gemini AI based on text instructions.

    Args:
        image_path: Path to the image to edit
        prompt: Text instructions for how to edit the image (e.g., "make the sky more blue", "add a cat")
        model: Gemini model (gemini-2.5-flash-image for speed, gemini-3-pro-image-preview for quality)
        output_path: Optional custom output path for the edited image

    Returns:
        Path to the edited image
    """
    return await edit_image(image_path, prompt, model, output_path)


@mcp.tool()
async def gemini_generate_with_references(
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
        reference_images: List of paths to reference images (max 3 for flash, max 14 for pro)
        model: Gemini model (gemini-2.5-flash-image or gemini-3-pro-image-preview)
        aspect_ratio: Image aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
        resolution: Image resolution (1K, 2K, 4K)
        output_path: Optional custom output path for the generated image

    Returns:
        Path to the generated image
    """
    return await generate_with_references(prompt, reference_images, model, aspect_ratio, resolution, output_path)


@mcp.tool()
async def gemini_describe_image(
    image_path: str,
    detail_level: str = "detailed",
) -> str:
    """
    Get an AI-generated description of an image.

    Args:
        image_path: Path to the image to describe
        detail_level: Level of detail (brief, detailed, technical)

    Returns:
        Text description of the image
    """
    return await describe_image(image_path, detail_level)


# ============================================================================
# ImageMagick Tools (Non-AI)
# ============================================================================


@mcp.tool()
def im_resize(
    image_path: str,
    width: int | None = None,
    height: int | None = None,
    maintain_aspect: bool = True,
    output_path: str | None = None,
) -> str:
    """
    Resize an image to specified dimensions using ImageMagick.

    Args:
        image_path: Path to the image to resize
        width: Target width in pixels
        height: Target height in pixels
        maintain_aspect: If True, maintain aspect ratio
        output_path: Optional custom output path

    Returns:
        Path to the resized image
    """
    return resize_image(image_path, width, height, maintain_aspect, output_path)


@mcp.tool()
def im_crop(
    image_path: str,
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
    width: int | None = None,
    height: int | None = None,
    gravity: str = "center",
    output_path: str | None = None,
) -> str:
    """
    Crop an image using ImageMagick.

    Two modes:
    1. Absolute: left, top, right, bottom coordinates
    2. Gravity: width, height, gravity (center, north, south, east, west)

    Args:
        image_path: Path to the image to crop
        left: Left coordinate (absolute mode)
        top: Top coordinate (absolute mode)
        right: Right coordinate (absolute mode)
        bottom: Bottom coordinate (absolute mode)
        width: Width (gravity mode)
        height: Height (gravity mode)
        gravity: Gravity position (gravity mode)
        output_path: Optional custom output path

    Returns:
        Path to the cropped image
    """
    return crop_image(image_path, left, top, right, bottom, width, height, gravity, output_path)


@mcp.tool()
def im_rotate(
    image_path: str,
    degrees: float,
    background_color: str = "transparent",
    output_path: str | None = None,
) -> str:
    """
    Rotate an image by specified degrees using ImageMagick.

    Args:
        image_path: Path to the image to rotate
        degrees: Rotation angle in degrees (positive = clockwise)
        background_color: Background color for exposed areas (transparent, white, black, #hex)
        output_path: Optional custom output path

    Returns:
        Path to the rotated image
    """
    return rotate_image(image_path, degrees, background_color, output_path)


@mcp.tool()
def im_flip(
    image_path: str,
    direction: str = "horizontal",
    output_path: str | None = None,
) -> str:
    """
    Flip an image horizontally or vertically using ImageMagick.

    Args:
        image_path: Path to the image to flip
        direction: Flip direction (horizontal or vertical)
        output_path: Optional custom output path

    Returns:
        Path to the flipped image
    """
    return flip_image(image_path, direction, output_path)


@mcp.tool()
def im_convert(
    image_path: str,
    target_format: str,
    quality: int = 90,
    output_path: str | None = None,
) -> str:
    """
    Convert an image to a different format using ImageMagick.

    Args:
        image_path: Path to the image to convert
        target_format: Target format (png, jpg, jpeg, webp, gif, bmp, tiff)
        quality: Quality for lossy formats (1-100)
        output_path: Optional custom output path

    Returns:
        Path to the converted image
    """
    return convert_format(image_path, target_format, quality, output_path)


@mcp.tool()
def im_effects(
    image_path: str,
    blur: float | None = None,
    sharpen: float | None = None,
    brightness: float | None = None,
    contrast: float | None = None,
    saturation: float | None = None,
    grayscale: bool = False,
    sepia: bool = False,
    negative: bool = False,
    output_path: str | None = None,
) -> str:
    """
    Apply various effects to an image using ImageMagick.

    Args:
        image_path: Path to the image
        blur: Blur radius (0-100)
        sharpen: Sharpen radius (0-100)
        brightness: Brightness adjustment (-100 to 100)
        contrast: Contrast adjustment (-100 to 100)
        saturation: Saturation adjustment (-100 to 100)
        grayscale: Convert to grayscale
        sepia: Apply sepia tone
        negative: Invert colors
        output_path: Optional custom output path

    Returns:
        Path to the processed image
    """
    return apply_effects(image_path, blur, sharpen, brightness, contrast, saturation, grayscale, sepia, negative, output_path)


@mcp.tool()
def im_composite(
    base_image: str,
    overlay_image: str,
    position_x: int = 0,
    position_y: int = 0,
    opacity: float = 1.0,
    output_path: str | None = None,
) -> str:
    """
    Overlay one image onto another using ImageMagick.

    Args:
        base_image: Path to the base image
        overlay_image: Path to the overlay image
        position_x: X position for overlay (from left)
        position_y: Y position for overlay (from top)
        opacity: Opacity of overlay (0.0 to 1.0)
        output_path: Optional custom output path

    Returns:
        Path to the composited image
    """
    return composite_images(base_image, overlay_image, position_x, position_y, opacity, output_path)


@mcp.tool()
def im_thumbnail(
    image_path: str,
    size: int = 256,
    output_path: str | None = None,
) -> str:
    """
    Create a square thumbnail using ImageMagick.

    Args:
        image_path: Path to the image
        size: Thumbnail size (square)
        output_path: Optional custom output path

    Returns:
        Path to the thumbnail
    """
    return create_thumbnail(image_path, size, output_path)


@mcp.tool()
def im_info(image_path: str) -> str:
    """
    Get detailed information about an image using ImageMagick.

    Args:
        image_path: Path to the image

    Returns:
        Detailed image information (dimensions, format, colorspace, etc.)
    """
    return get_image_info(image_path)


@mcp.tool()
def im_border(
    image_path: str,
    border_size: int = 10,
    border_color: str = "black",
    output_path: str | None = None,
) -> str:
    """
    Add a border around an image using ImageMagick.

    Args:
        image_path: Path to the image
        border_size: Border width in pixels
        border_color: Border color (name or #hex)
        output_path: Optional custom output path

    Returns:
        Path to the image with border
    """
    return add_border(image_path, border_size, border_color, output_path)


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
