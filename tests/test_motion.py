from pathlib import Path
import pytest
from product2ad.motion.browser import build_motion_html

def test_motion_html(tmp_path):
    source=tmp_path/'a.png';source.write_bytes(b'fake')
    result=Path(build_motion_html(source,tmp_path/'demo.html',duration=5))
    data=result.read_text()
    assert 'window.renderAt' in data
    assert 'data:image/png;base64,' in data
    assert 'THE REVEAL' in data

def test_invalid_duration(tmp_path):
    source=tmp_path/'a.png';source.write_bytes(b'fake')
    with pytest.raises(ValueError): build_motion_html(source,tmp_path/'demo.html',duration=0)

def test_missing_image(tmp_path):
    with pytest.raises(FileNotFoundError): build_motion_html(tmp_path/'missing.png',tmp_path/'demo.html')
