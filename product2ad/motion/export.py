"""Deterministic HTML-to-MP4 export using installed Chromium and FFmpeg.

No external network resources are needed. Frame times are driven by renderAt(t),
not browser wall-clock playback.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile


def export_motion(html_path, output, *, duration=7.0, fps=24, width=540, height=960, chromium=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError('Install playwright: pip install playwright') from exc
    source = Path(html_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() != '.html':
        raise ValueError('Expected an HTML source file')
    if not (0.5 <= duration <= 120 and 1 <= fps <= 60):
        raise ValueError('Invalid duration or fps')
    if not (240 <= width <= 1920 and 240 <= height <= 1920):
        raise ValueError('Invalid output dimensions')
    if not shutil.which('ffmpeg'):
        raise RuntimeError('ffmpeg is required for MP4 export')
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='product2ad-frames-') as tmp:
        folder = Path(tmp)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=chromium or shutil.which('chromium') or shutil.which('google-chrome'),
                headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            try:
                page = browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,
                                        reduced_motion='reduce')
                page.set_content(source.read_text(encoding='utf-8'), wait_until='load')
                page.wait_for_function('window.product2adReady === true', timeout=15000)
                count = round(duration*fps)
                for index in range(count):
                    t = index/fps
                    page.evaluate('(t) => window.renderAt(t)',t)
                    page.screenshot(path=str(folder / f'frame-{index:05d}.png'), animations='disabled')
            finally:
                browser.close()
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),
             '-i',str(folder/'frame-%05d.png'),'-c:v','libx264','-pix_fmt','yuv420p',
             '-movflags','+faststart','-crf','19',str(output)]
        result=subprocess.run(cmd,capture_output=True,text=True)
        if result.returncode:
            raise RuntimeError('ffmpeg export failed: '+result.stderr[-1000:])
    probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                          '-of','json',str(output)],capture_output=True,text=True)
    if probe.returncode:
        raise RuntimeError('ffprobe failed: '+probe.stderr[-500:])
    actual=float(json.loads(probe.stdout)['format']['duration'])
    if abs(actual-duration)>1/fps+0.02:
        raise RuntimeError(f'Incorrect output duration: {actual} vs {duration}')
    return {'output':str(output),'duration':actual,'frames':round(duration*fps),'fps':fps,
            'width':width,'height':height}
