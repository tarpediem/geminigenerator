# Gemini MCP - Image Generation Server

MCP (Model Context Protocol) server for image generation and editing using Google's Gemini API and ImageMagick.

## Quick Install for AI Assistants

> **AI Assistant Instructions**: Follow these steps to install this MCP server for the user. You will need to ask the user for their Gemini API key.

### Step 1: Check Prerequisites

```bash
# Check Python version (needs 3.10+)
python3 --version

# Check if ImageMagick is installed
magick --version || convert --version

# Check if uv is installed
uv --version
```

**If ImageMagick is missing:**
- Arch/CachyOS: `sudo pacman -S imagemagick`
- Ubuntu/Debian: `sudo apt install imagemagick`
- macOS: `brew install imagemagick`

**If uv is missing:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Clone and Install

```bash
# Clone the repository
git clone https://github.com/tarpediem/geminigenerator.git
cd geminigenerator

# Create virtual environment and install
uv venv
uv pip install -e .
```

### Step 3: Get the Installation Path

```bash
# Get the absolute path (you'll need this)
pwd
```

### Step 4: Ask User for API Key

> **AI: Ask the user**: "Please provide your Gemini API key. You can get one free at https://aistudio.google.com/apikey"

### Step 5: Configure Claude Code

The MCP configuration file location depends on the system:
- **Linux**: `~/.config/claude-code/settings.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add or merge this configuration (replace `INSTALLATION_PATH` and `YOUR_API_KEY`):

```json
{
  "mcpServers": {
    "gemini-image": {
      "command": "uv",
      "args": [
        "--directory",
        "INSTALLATION_PATH",
        "run",
        "python",
        "-m",
        "gemini_mcp.server"
      ],
      "env": {
        "GEMINI_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

### Step 6: Restart Claude Code

Tell the user to restart Claude Code to load the new MCP server.

### Step 7: Verify Installation

After restart, the following tools should be available:
- `gemini_generate_image`
- `gemini_edit_image`
- `gemini_generate_with_references`
- `gemini_describe_image`
- `im_resize`, `im_crop`, `im_rotate`, `im_flip`, `im_convert`, `im_effects`, `im_composite`, `im_thumbnail`, `im_info`, `im_border`

---

## Features

### Gemini AI Tools
| Tool | Description |
|------|-------------|
| `gemini_generate_image` | Generate images from text prompts |
| `gemini_edit_image` | Edit existing images with text instructions |
| `gemini_generate_with_references` | Generate using reference images for style guidance |
| `gemini_describe_image` | Get AI-powered image descriptions |

### ImageMagick Tools (Non-AI, Local Processing)
| Tool | Description |
|------|-------------|
| `im_resize` | Resize images with aspect ratio control |
| `im_crop` | Crop images (absolute coordinates or gravity-based) |
| `im_rotate` | Rotate images by any angle |
| `im_flip` | Flip horizontally or vertically |
| `im_convert` | Convert between formats (png, jpg, webp, gif, bmp, tiff) |
| `im_effects` | Apply effects (blur, sharpen, brightness, contrast, grayscale, sepia, negative) |
| `im_composite` | Overlay one image onto another |
| `im_thumbnail` | Create square thumbnails |
| `im_info` | Get image metadata (dimensions, format, colorspace, etc.) |
| `im_border` | Add borders around images |

## Available Models

| Model | Speed | Quality | Max Reference Images | Best For |
|-------|-------|---------|---------------------|----------|
| `gemini-2.5-flash-image` | Fast (~3-6s) | Good | 3 | Quick iterations, drafts |
| `gemini-3-pro-image-preview` | Slower | Excellent (4K) | 14 | Final assets, complex compositions |

## Supported Parameters

### Aspect Ratios
`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

### Resolutions
- `1K` - 1024px (default, fastest)
- `2K` - 2048px
- `4K` - 4096px (gemini-3-pro only)

## Usage Examples

### Generate an image
```
Generate a cyberpunk cityscape at sunset, neon lights reflecting on wet streets
```

### Edit an existing image
```
Edit /path/to/image.png: add a rainbow in the sky
```

### Generate with style reference
```
Generate a portrait in the style of the reference images: [/path/to/style1.png, /path/to/style2.png]
```

### Batch processing with ImageMagick
```
Resize all images in /photos to 800px width, convert to webp, add 5px white border
```

## Manual Installation

```bash
git clone https://github.com/tarpediem/geminigenerator.git
cd geminigenerator
uv venv && uv pip install -e .
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Your Google AI Studio API key |
| `DEFAULT_OUTPUT_DIR` | No | `./output` | Default directory for generated images |
| `DEFAULT_MODEL` | No | `gemini-2.5-flash-image` | Default model for generation |
| `DEFAULT_RESOLUTION` | No | `1K` | Default resolution |
| `DEFAULT_ASPECT_RATIO` | No | `1:1` | Default aspect ratio |

## Troubleshooting

### "GEMINI_API_KEY not set"
Ensure the API key is set in the MCP configuration's `env` block.

### "ImageMagick not found"
Install ImageMagick for your system (see prerequisites).

### "Module not found"
Run `uv pip install -e .` in the project directory.

## License

MIT

## Credits

Built with [FastMCP](https://github.com/jlowin/fastmcp), [google-genai](https://github.com/googleapis/python-genai), and [Wand](https://docs.wand-py.org/).
