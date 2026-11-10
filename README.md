# Product2Ad

**An experimental, open-source agent skill, CLI, and MCP toolkit for turning a product image into an editable ad plan and motion-graphics video.**

> **Project status: experimental v0.1.** The CPU and browser renderers move and composite an input image. They **do not** produce photorealistic generative-video commercials. The Blender can-scene renderer is a prototype and has not been visually validated. The browser animation is an independent implementation influenced by ideas in [Bang Motion](https://github.com/bangtutorial/bang-motion), **not** its upstream code or a direct integration.

## Features

- Image + prompt → structured six-shot storyboard JSON and variable-duration MP4 via a CPU renderer
- Experimental browser motion HTML with deterministic `window.renderAt(seconds)` and an FFmpeg/Chromium MP4 export path
- Experimental Blender 4.x 3D can scene with a curved front-facing image and procedural droplets
- Local reference-video analysis (cuts, motion estimates, average color) for authorized footage
- Agent instructions in [`skills/product2ad/SKILL.md`](skills/product2ad/SKILL.md), a Python CLI, and optional stdio MCP tools (`create_ad_plan`, `render_ad`)

## Setup

Requirements: Python 3.10+, FFmpeg on PATH. Additional dependencies are needed for optional backends.

```bash
git clone https://github.com/santosh1664/Product2Ad.git
cd Product2Ad
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e '.[test]'
python -m pytest -q
```

## Create your first ad

The included `examples/sample-product.png` is original demo artwork.

```bash
product2ad plan --image examples/sample-product.png --prompt "Fresh water bottle reveal" --duration 7
product2ad render --image examples/sample-product.png --prompt "Fresh water bottle reveal" --duration 7 --output outputs/ad.mp4
```

The resulting `outputs/ad.mp4` is a *simple motion-graphics preview*, not cinematic AI footage. The editable storyboard is written to `outputs/ad.json`. Duration is user-selectable (1–120 seconds in the CPU renderer); it is not fixed to 30 seconds.

## Browser-motion animation and MP4 export

Install Playwright and a Chromium binary (plus FFmpeg and FFprobe):

```bash
pip install playwright
playwright install chromium
product2ad render-motion --image examples/sample-product.png --duration 5 --output outputs/motion.html
product2ad export-motion --html outputs/motion.html --duration 5 --fps 15 --width 360 --height 640 --output outputs/motion.mp4
```

The exporter tries to use a system `chromium` or `google-chrome` executable. On systems with only Playwright-installed Chromium, pass or configure a browser executable as appropriate; currently the CLI does not expose `--chromium`. Generated HTML is standalone and self-contained. It uses CSS transforms and is not a true 3D reconstruction.

## Blender 3D can prototype

Needs Blender 4.x and FFmpeg (Blender is **not** bundled):

```bash
product2ad render-3d --image examples/sample-product.png --dry-run
product2ad render-3d --image examples/sample-product.png --duration 5 --samples 16 --output outputs/can.mp4
```

The scene maps a source image to a curved front-facing section; it cannot recover an accurate full label wrap or unseen sides from one photo. **No successful Blender visual render has been verified by this project release.** The prototype is not a photorealistic commercial generator.

## Analyze a local reference

With OpenCV and NumPy installed:

```bash
pip install opencv-python numpy
product2ad analyze-reference --video /path/to/your-licensed-reference.mp4 --output outputs/analysis.json
```

This performs basic video analysis, **not** model training. Obtain appropriate permissions for third-party footage.

## Claude Code / Codex and MCP

The project includes an agent skill file at [`skills/product2ad/SKILL.md`](skills/product2ad/SKILL.md). Install it in your agent's supported skills directory and install the CLI in that execution environment. Compatible agents can use the optional stdio MCP server:

```bash
pip install -e '.[mcp]'
product2ad-mcp
```

Register `product2ad-mcp` in the coding agent's MCP configuration. The server currently exposes `create_ad_plan` and `render_ad` for the basic CPU renderer. It does **not** automatically install into ordinary ChatGPT conversations or add an AI video model.

## Tests

```bash
pip install -e '.[test]'
pytest -q
```

Some optional backend tests skip when external software is missing. Tests for CLI parameters or MP4 metadata are not a guarantee of cinematic visual quality.

## Architecture

`SKILL.md → coding agent → Python CLI / MCP → planner + renderer → MP4 and JSON`

Optional render paths: Blender can prototype and standalone browser motion → Chromium frames → FFmpeg MP4.

## Limitations / next milestones

1. Fully validate Blender rendering and product geometry with real frames.
2. Add an image-to-video provider and frame-by-frame quality checks.
3. Integrate and test real upstream Bang Motion tooling if appropriate, preserving its licenses.
4. Add audio, per-scene repair, reliable branding fidelity, and reference-guided creative direction.
5. Improve installer and agent-specific setup and preview support.

## License

Source code: MIT, see [LICENSE](LICENSE). The original sample artwork is included for demonstration. Do not assume external product logos, reference footage, or model weights are licensed for redistribution or training.
