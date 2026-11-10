import pytest
from pathlib import Path
from product2ad.core import plan,render

def test_plan():
    p=plan('sample.png','premium',30)
    assert len(p['shots'])==6
    assert sum(s['duration'] for s in p['shots'])==30

def test_bad_duration():
    with pytest.raises(ValueError):plan('sample.png','x',0)

def test_missing_image(tmp_path):
    with pytest.raises(FileNotFoundError):render(str(tmp_path/'missing.png'),'x',str(tmp_path/'out.mp4'))

def test_render(tmp_path):
    from PIL import Image
    image=tmp_path/'input.png';Image.new('RGBA',(100,200),(255,150,40,255)).save(image)
    output=tmp_path/'out.mp4'
    render(str(image),'test',str(output),duration=1,width=128,height=224,fps=4)
    assert output.exists() and output.stat().st_size>1000
    assert output.with_suffix('.json').exists()
