"""Reference-video analysis: reproducible shot boundaries and motion statistics.

Does not copy frames into a training dataset or fine-tune model weights.
"""
from __future__ import annotations
import json
from pathlib import Path


def analyze_reference(video: str, output: str | None = None, sample_fps: float = 2.0, threshold: float = 0.38) -> dict:
    import cv2
    import numpy as np
    source = Path(video).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f'Reference video not found: {source}')
    if not (0.5 <= sample_fps <= 10):
        raise ValueError('sample_fps must be between 0.5 and 10')
    if not (0.05 <= threshold <= 1):
        raise ValueError('threshold must be between 0.05 and 1')
    cap = cv2.VideoCapture(str(source))
    try:
        if not cap.isOpened():
            raise ValueError('Cannot decode reference video')
        fps = cap.get(cv2.CAP_PROP_FPS)
        count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if fps <= 0 or count <= 0:
            raise ValueError('Reference video has invalid timing')
        duration = count / fps
        stride = max(1, round(fps / sample_fps))
        previous_hist = None
        previous_gray = None
        cuts = [0.0]
        samples = 0
        motion = []
        colors = []
        for idx in range(0, int(count), stride):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                break
            small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [24, 16], [0, 180, 0, 256])
            cv2.normalize(hist, hist)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            if previous_hist is not None:
                difference = cv2.compareHist(previous_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
                if difference >= threshold and idx/fps-cuts[-1] >= 0.4:
                    cuts.append(round(idx/fps, 3))
                motion.append(float(np.mean(cv2.absdiff(gray, previous_gray)) / 255.0))
            colors.append(cv2.cvtColor(small, cv2.COLOR_BGR2RGB).mean(axis=(0, 1)))
            previous_hist, previous_gray = hist, gray
            samples += 1
        if samples == 0:
            raise ValueError('No video frames decoded')
        boundaries = cuts + [round(duration, 3)]
        shots = [{'start': boundaries[i], 'end': boundaries[i+1], 'duration': round(boundaries[i+1]-boundaries[i], 3)} for i in range(len(boundaries)-1)]
        rgb = np.mean(colors, axis=0)
        result = {'source': str(source), 'duration_seconds': round(duration, 3),
                  'resolution': [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))],
                  'sampled_frames': samples, 'shots': shots,
                  'mean_frame_change': round(float(np.mean(motion)), 4) if motion else 0,
                  'mean_rgb': [round(float(v)) for v in rgb],
                  'limitations': 'Cuts and frame differences are heuristic; no semantic camera, material, or object understanding. No training performed.'}
        if output:
            target = Path(output).expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(result, indent=2), encoding='utf-8')
        return result
    finally:
        cap.release()
