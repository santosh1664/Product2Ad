import subprocess
from pathlib import Path
import pytest
from product2ad.reference_analysis import analyze_reference

def test_missing_video():
    with pytest.raises(FileNotFoundError):
        analyze_reference('/nonexistent/reference.mp4')

def test_invalid_sample_rate(tmp_path):
    p = tmp_path/'clip.mp4'
    p.write_bytes(b'placeholder')
    with pytest.raises(ValueError):
        analyze_reference(str(p), sample_fps=0)

def test_real_video(tmp_path):
    source = Path(__file__).resolve().parents[1] / 'examples' / 'demo.mp4'
    if not source.exists():
        pytest.skip('demo clip not available')
    result = analyze_reference(str(source), str(tmp_path/'analysis.json'))
    assert result['duration_seconds'] > 0
    assert result['shots']
    assert (tmp_path/'analysis.json').exists()
