from pathlib import Path
import pytest
from product2ad.blender_pipeline import build_job, render_blender

@pytest.fixture
def sample(tmp_path):
    p=tmp_path/'product.png'
    p.write_bytes(b'example')
    return p

def test_job(sample,tmp_path):
    job=build_job(str(sample),str(tmp_path/'ad.mp4'))
    assert job['duration']==5 and job['fps']==24
    assert job['image']==str(sample)

def test_invalid_dimensions(sample,tmp_path):
    with pytest.raises(ValueError):
        build_job(str(sample),str(tmp_path/'ad.mp4'),width=721)

def test_missing_product(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_job(str(tmp_path/'missing.png'),str(tmp_path/'ad.mp4'))

def test_dry_run_without_blender(sample,tmp_path):
    out=tmp_path/'ad.mp4'
    assert render_blender(str(sample),str(out),dry_run=True)==out
    assert not out.exists()

def test_missing_blender_is_actionable(sample,tmp_path):
    with pytest.raises(RuntimeError, match='Blender not installed'):
        render_blender(str(sample),str(tmp_path/'ad.mp4'),blender='not-a-real-blender-executable')
