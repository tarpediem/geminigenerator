"""Utility functions for Gemini MCP server."""

import base64
import logging
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (never use print for STDIO MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gemini-mcp")


def get_output_dir() -> Path:
    """Get the default output directory, creating it if needed."""
    output_dir = Path(os.getenv("DEFAULT_OUTPUT_DIR", "./output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a safe filename slug."""
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase and replace spaces/special chars
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:max_length]


def generate_filename(prompt: str, extension: str = "png") -> str:
    """Generate a filename based on prompt and timestamp."""
    slug = slugify(prompt)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{slug}_{timestamp}.{extension}"


def get_output_path(prompt: str, output_path: str | None = None, extension: str = "png") -> Path:
    """Get the full output path for an image."""
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    output_dir = get_output_dir()
    filename = generate_filename(prompt, extension)
    return output_dir / filename


def image_to_base64(image_path: str | Path) -> str:
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def base64_to_image(base64_string: str, output_path: str | Path) -> Path:
    """Save a base64 string as an image file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_string))

    return path


def get_mime_type(file_path: str | Path) -> str:
    """Get MIME type from file extension."""
    extension = Path(file_path).suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }
    return mime_types.get(extension, "image/png")


def validate_aspect_ratio(aspect_ratio: str) -> str:
    """Validate and return aspect ratio."""
    valid_ratios = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
    if aspect_ratio not in valid_ratios:
        logger.warning(f"Invalid aspect ratio '{aspect_ratio}', defaulting to 1:1")
        return "1:1"
    return aspect_ratio


def validate_resolution(resolution: str) -> str:
    """Validate and return resolution."""
    valid_resolutions = ["1K", "2K", "4K"]
    resolution = resolution.upper()
    if resolution not in valid_resolutions:
        logger.warning(f"Invalid resolution '{resolution}', defaulting to 1K")
        return "1K"
    return resolution


def validate_model(model: str) -> str:
    """Validate and return model name."""
    valid_models = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
    if model not in valid_models:
        logger.warning(f"Invalid model '{model}', defaulting to gemini-2.5-flash-image")
        return "gemini-2.5-flash-image"
    return model


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
