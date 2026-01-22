# Gemini MCP - Image Generation Server

MCP (Model Context Protocol) server for image generation and editing using Google's Gemini API and ImageMagick.

## Features

### Gemini AI Tools
- **gemini_generate_image** - Generate images from text prompts
- **gemini_edit_image** - Edit existing images with text instructions
- **gemini_generate_with_references** - Generate images using reference images for style guidance
- **gemini_describe_image** - Get AI-powered image descriptions

### ImageMagick Tools (Non-AI)
- **im_resize** - Resize images
- **im_crop** - Crop images (absolute or gravity-based)
- **im_rotate** - Rotate images
- **im_flip** - Flip images horizontally/vertically
- **im_convert** - Convert between formats (png, jpg, webp, gif, etc.)
- **im_effects** - Apply effects (blur, sharpen, brightness, contrast, grayscale, sepia, negative)
- **im_composite** - Overlay images
- **im_thumbnail** - Create thumbnails
- **im_info** - Get image metadata
- **im_border** - Add borders

## Prerequisites

- Python 3.10+
- ImageMagick 7.x
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Installation

```bash
# Clone the repository
git clone https://github.com/tarpediem/geminigenerator.git
cd geminigenerator

# Install with uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Or with pip
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

## Usage with Claude Code

Add to your `~/.config/claude-code/settings.json`:

```json
{
  "mcpServers": {
    "gemini-image": {
      "command": "uv",
      "args": ["--directory", "/path/to/geminigenerator", "run", "python", "-m", "gemini_mcp.server"],
      "env": {
        "GEMINI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or run directly:
```bash
uv run python -m gemini_mcp.server
```

## Available Models

| Model | Speed | Quality | Max References |
|-------|-------|---------|----------------|
| `gemini-2.5-flash-image` | Fast | Good | 3 |
| `gemini-3-pro-image-preview` | Slower | Excellent | 14 |

## Supported Parameters

### Aspect Ratios
`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

### Resolutions
`1K`, `2K`, `4K`

## License

MIT
