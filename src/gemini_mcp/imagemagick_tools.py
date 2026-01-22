"""ImageMagick tools for non-AI image manipulation using Wand."""

from pathlib import Path

from wand.color import Color
from wand.image import Image

from .utils import format_file_size, get_output_path, logger


def resize_image(
    image_path: str,
    width: int | None = None,
    height: int | None = None,
    maintain_aspect: bool = True,
    output_path: str | None = None,
) -> str:
    """
    Resize an image to specified dimensions.

    Args:
        image_path: Path to the image to resize
        width: Target width in pixels (optional if height is provided)
        height: Target height in pixels (optional if width is provided)
        maintain_aspect: If True, maintain aspect ratio when only one dimension is specified
        output_path: Optional custom output path

    Returns:
        Path to the resized image
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    if width is None and height is None:
        return "Error: At least one of width or height must be specified"

    with Image(filename=image_path) as img:
        original_size = f"{img.width}x{img.height}"

        if maintain_aspect:
            if width and not height:
                height = int(img.height * (width / img.width))
            elif height and not width:
                width = int(img.width * (height / img.height))

        img.resize(width or img.width, height or img.height)

        final_path = get_output_path(f"resized_{width}x{height}", output_path, Path(image_path).suffix[1:])
        img.save(filename=str(final_path))

        logger.info(f"Resized {original_size} -> {img.width}x{img.height}: {final_path}")

    return f"Image resized from {original_size} to {width}x{height}. Saved to: {final_path}"


def crop_image(
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
    Crop an image to specified region.

    Can be used in two modes:
    1. Absolute coordinates: left, top, right, bottom
    2. Gravity-based: width, height, gravity (center, north, south, east, west, etc.)

    Args:
        image_path: Path to the image to crop
        left: Left coordinate for absolute crop
        top: Top coordinate for absolute crop
        right: Right coordinate for absolute crop
        bottom: Bottom coordinate for absolute crop
        width: Width for gravity-based crop
        height: Height for gravity-based crop
        gravity: Gravity for crop (center, north, south, east, west, north_east, etc.)
        output_path: Optional custom output path

    Returns:
        Path to the cropped image
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    with Image(filename=image_path) as img:
        original_size = f"{img.width}x{img.height}"

        if all(v is not None for v in [left, top, right, bottom]):
            # Absolute coordinate crop
            img.crop(left=left, top=top, right=right, bottom=bottom)
        elif width is not None and height is not None:
            # Gravity-based crop
            img.crop(width=width, height=height, gravity=gravity)
        else:
            return "Error: Provide either (left, top, right, bottom) or (width, height, gravity)"

        final_path = get_output_path(f"cropped_{img.width}x{img.height}", output_path, Path(image_path).suffix[1:])
        img.save(filename=str(final_path))

        logger.info(f"Cropped {original_size} -> {img.width}x{img.height}: {final_path}")

    return f"Image cropped from {original_size} to {img.width}x{img.height}. Saved to: {final_path}"


def rotate_image(
    image_path: str,
    degrees: float,
    background_color: str = "transparent",
    output_path: str | None = None,
) -> str:
    """
    Rotate an image by specified degrees.

    Args:
        image_path: Path to the image to rotate
        degrees: Rotation angle in degrees (positive = clockwise)
        background_color: Background color for areas exposed by rotation (transparent, white, black, #hex)
        output_path: Optional custom output path

    Returns:
        Path to the rotated image
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    with Image(filename=image_path) as img:
        with Color(background_color) as bg:
            img.rotate(degrees, background=bg)

        final_path = get_output_path(f"rotated_{degrees}deg", output_path, "png")  # PNG for transparency
        img.save(filename=str(final_path))

        logger.info(f"Rotated {degrees} degrees: {final_path}")

    return f"Image rotated {degrees} degrees. Saved to: {final_path}"


def flip_image(
    image_path: str,
    direction: str = "horizontal",
    output_path: str | None = None,
) -> str:
    """
    Flip an image horizontally or vertically.

    Args:
        image_path: Path to the image to flip
        direction: Flip direction (horizontal or vertical)
        output_path: Optional custom output path

    Returns:
        Path to the flipped image
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    if direction not in ["horizontal", "vertical"]:
        return "Error: Direction must be 'horizontal' or 'vertical'"

    with Image(filename=image_path) as img:
        if direction == "horizontal":
            img.flop()  # Horizontal flip
        else:
            img.flip()  # Vertical flip

        final_path = get_output_path(f"flipped_{direction}", output_path, Path(image_path).suffix[1:])
        img.save(filename=str(final_path))

        logger.info(f"Flipped {direction}: {final_path}")

    return f"Image flipped {direction}. Saved to: {final_path}"


def convert_format(
    image_path: str,
    target_format: str,
    quality: int = 90,
    output_path: str | None = None,
) -> str:
    """
    Convert an image to a different format.

    Args:
        image_path: Path to the image to convert
        target_format: Target format (png, jpg, jpeg, webp, gif, bmp, tiff)
        quality: Quality for lossy formats (1-100)
        output_path: Optional custom output path

    Returns:
        Path to the converted image
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    valid_formats = ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff"]
    target_format = target_format.lower()
    if target_format not in valid_formats:
        return f"Error: Invalid format. Supported: {valid_formats}"

    with Image(filename=image_path) as img:
        img.format = target_format
        if target_format in ["jpg", "jpeg", "webp"]:
            img.compression_quality = quality

        final_path = get_output_path(f"converted", output_path, target_format)
        img.save(filename=str(final_path))

        logger.info(f"Converted to {target_format}: {final_path}")

    return f"Image converted to {target_format}. Saved to: {final_path}"


def apply_effects(
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
    Apply various effects to an image.

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
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    effects_applied = []

    with Image(filename=image_path) as img:
        if blur is not None:
            img.gaussian_blur(sigma=blur)
            effects_applied.append(f"blur({blur})")

        if sharpen is not None:
            img.sharpen(radius=0, sigma=sharpen)
            effects_applied.append(f"sharpen({sharpen})")

        if brightness is not None:
            img.modulate(brightness=100 + brightness)
            effects_applied.append(f"brightness({brightness})")

        if contrast is not None:
            # Wand uses a different scale for contrast
            img.contrast_stretch(black_point=max(0, -contrast / 100), white_point=max(0, contrast / 100))
            effects_applied.append(f"contrast({contrast})")

        if saturation is not None:
            img.modulate(saturation=100 + saturation)
            effects_applied.append(f"saturation({saturation})")

        if grayscale:
            img.transform_colorspace("gray")
            effects_applied.append("grayscale")

        if sepia:
            img.sepia_tone(threshold=0.8)
            effects_applied.append("sepia")

        if negative:
            img.negate()
            effects_applied.append("negative")

        if not effects_applied:
            return "Error: No effects specified"

        effect_name = "_".join(effects_applied[:3])  # Limit filename length
        final_path = get_output_path(f"effects_{effect_name}", output_path, Path(image_path).suffix[1:])
        img.save(filename=str(final_path))

        logger.info(f"Applied effects {effects_applied}: {final_path}")

    return f"Applied effects: {', '.join(effects_applied)}. Saved to: {final_path}"


def composite_images(
    base_image: str,
    overlay_image: str,
    position_x: int = 0,
    position_y: int = 0,
    opacity: float = 1.0,
    output_path: str | None = None,
) -> str:
    """
    Composite (overlay) one image onto another.

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
    if not Path(base_image).exists():
        return f"Error: Base image not found: {base_image}"
    if not Path(overlay_image).exists():
        return f"Error: Overlay image not found: {overlay_image}"

    with Image(filename=base_image) as base:
        with Image(filename=overlay_image) as overlay:
            if opacity < 1.0:
                overlay.transparentize(1.0 - opacity)

            base.composite(overlay, left=position_x, top=position_y)

        final_path = get_output_path("composited", output_path, "png")
        base.save(filename=str(final_path))

        logger.info(f"Composited images: {final_path}")

    return f"Images composited. Saved to: {final_path}"


def create_thumbnail(
    image_path: str,
    size: int = 256,
    output_path: str | None = None,
) -> str:
    """
    Create a square thumbnail of an image.

    Args:
        image_path: Path to the image
        size: Thumbnail size (creates a square thumbnail)
        output_path: Optional custom output path

    Returns:
        Path to the thumbnail
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    with Image(filename=image_path) as img:
        img.transform(resize=f"{size}x{size}^")
        img.crop(width=size, height=size, gravity="center")

        final_path = get_output_path(f"thumb_{size}", output_path, Path(image_path).suffix[1:])
        img.save(filename=str(final_path))

        logger.info(f"Created thumbnail {size}x{size}: {final_path}")

    return f"Thumbnail created ({size}x{size}). Saved to: {final_path}"


def get_image_info(image_path: str) -> str:
    """
    Get detailed information about an image.

    Args:
        image_path: Path to the image

    Returns:
        Detailed image information
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    file_size = Path(image_path).stat().st_size

    with Image(filename=image_path) as img:
        info = {
            "path": image_path,
            "format": img.format,
            "width": img.width,
            "height": img.height,
            "depth": img.depth,
            "colorspace": img.colorspace,
            "has_alpha": img.alpha_channel,
            "file_size": format_file_size(file_size),
            "resolution": f"{img.resolution[0]:.0f}x{img.resolution[1]:.0f} DPI" if img.resolution else "Unknown",
        }

    info_str = "\n".join(f"  {k}: {v}" for k, v in info.items())
    return f"Image Information:\n{info_str}"


def add_border(
    image_path: str,
    border_size: int = 10,
    border_color: str = "black",
    output_path: str | None = None,
) -> str:
    """
    Add a border around an image.

    Args:
        image_path: Path to the image
        border_size: Border width in pixels
        border_color: Border color (name or #hex)
        output_path: Optional custom output path

    Returns:
        Path to the image with border
    """
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    with Image(filename=image_path) as img:
        with Color(border_color) as color:
            img.border(color, width=border_size, height=border_size)

        final_path = get_output_path(f"bordered_{border_size}px", output_path, Path(image_path).suffix[1:])
        img.save(filename=str(final_path))

        logger.info(f"Added {border_size}px border: {final_path}")

    return f"Added {border_size}px {border_color} border. Saved to: {final_path}"
