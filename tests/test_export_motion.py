import pytest
from product2ad.motion.export import export_motion

def test_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_motion(tmp_path/'missing.html',tmp_path/'out.mp4')

def test_invalid_parameters(tmp_path):
    html=tmp_path/'test.html';html.write_text('<html></html>')
    with pytest.raises(ValueError):
        export_motion(html,tmp_path/'out.mp4',fps=0)
    with pytest.raises(ValueError):
        export_motion(html,tmp_path/'out.mp4',duration=0)
    with pytest.raises(ValueError):
        export_motion(html,tmp_path/'out.mp4',width=100)

def test_end_to_end_browser_mp4(tmp_path):
    import shutil
    if not (shutil.which('chromium') and shutil.which('ffmpeg') and shutil.which('ffprobe')):
        pytest.skip('Chromium/FFmpeg unavailable')
    from PIL import Image
    from product2ad.motion.browser import build_motion_html
    img=tmp_path/'product.png'
    Image.new('RGBA',(80,160),(215,25,45,255)).save(img)
    html=tmp_path/'demo.html'
    build_motion_html(img,html,duration=2)
    result=export_motion(html,tmp_path/'demo.mp4',duration=2,fps=4,width=240,height=320)
    assert result['frames']==8
    assert (tmp_path/'demo.mp4').stat().st_size>1000
