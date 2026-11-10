"""Blender-based 3D ad renderer. Blender is an optional external dependency.

Uses an input product image as an approximate cylindrical texture. A single
front photo cannot reconstruct a complete accurate 360-degree product label.
"""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path


def build_job(image: str, output: str, *, duration: int = 5, fps: int = 24,
              width: int = 720, height: int = 1280, samples: int = 32) -> dict:
    source = Path(image).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Product image not found: {source}")
    if source.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
        raise ValueError('Product image must be PNG, JPG, JPEG or WebP')
    if not 1 <= duration <= 60 or not 12 <= fps <= 60:
        raise ValueError('duration must be 1–60 seconds; fps must be 12–60')
    if not 128 <= width <= 3840 or not 128 <= height <= 3840 or width % 2 or height % 2:
        raise ValueError('dimensions must be even and between 128 and 3840')
    if not 8 <= samples <= 256:
        raise ValueError('samples must be 8–256')
    return dict(image=str(source), output=str(Path(output).expanduser().resolve()),
                duration=duration, fps=fps, width=width, height=height, samples=samples)


def render_blender(image: str, output: str, *, blender: str = 'blender',
                   duration: int = 5, fps: int = 24, width: int = 720,
                   height: int = 1280, samples: int = 32, dry_run: bool = False) -> Path:
    job = build_job(image, output, duration=duration, fps=fps, width=width,
                    height=height, samples=samples)
    target = Path(job['output'])
    script = Path(__file__).parent / 'blender' / 'scene.py'
    if not script.is_file():
        raise RuntimeError(f'Missing Blender scene script: {script}')
    if dry_run:
        return target
    binary = shutil.which(blender)
    if not binary:
        raise RuntimeError('Blender not installed. Install Blender 4.x and retry, or use --dry-run to validate inputs.')
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is required for MP4 encoding')
    target.parent.mkdir(parents=True, exist_ok=True)
    jobfile = target.with_suffix('.job.json')
    jobfile.write_text(json.dumps(job, indent=2), encoding='utf-8')
    # Blender renders lossless PNG frames first; FFmpeg handles MP4 encoding.
    command = [binary, '--background', '--factory-startup', '--python', str(script), '--', str(jobfile)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=3600)
    if result.returncode:
        raise RuntimeError('Blender rendering failed:\n' + (result.stderr + '\n' + result.stdout)[-3500:])
    frames = target.with_suffix('.frames')
    ffmpeg = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(fps),
              '-i', str(frames / 'frame_%04d.png'), '-c:v', 'libx264', '-crf', '19',
              '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(target)]
    result = subprocess.run(ffmpeg, capture_output=True, text=True, timeout=600)
    if result.returncode or not target.is_file():
        raise RuntimeError('FFmpeg encoding failed: ' + result.stderr[-2500:])
    return target
