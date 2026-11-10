"""Deterministic, CPU-first ad generator. No external model calls."""
import json, math, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

STYLES = {'cinematic': ((9,18,35),(30,80,110)), 'fresh': ((7,59,72),(24,135,155)), 'bold': ((39,16,55),(130,42,90))}

def plan(product: str, prompt: str, duration: int=30, style: str='cinematic') -> dict:
    if not 1 <= duration <= 120: raise ValueError('duration must be 1–120 seconds')
    if style not in STYLES: raise ValueError('unknown style')
    return {'product':str(Path(product).resolve()), 'prompt':prompt, 'duration':duration,'style':style,
            'shots':[{'start':i*duration/6,'duration':duration/6,'name':name} for i,name in enumerate(['Reveal','Detail','Spotlight','Motion','Benefit','Hero'])]}

def font(size):
    path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    try: return ImageFont.truetype(path,size)
    except OSError: return ImageFont.load_default()

def frame(product, p, t, w, h):
    colors=STYLES[p['style']]; f=t/p['duration']; shot=min(5,int(f*6)); progress=(f*6)%1
    bg=Image.new('RGB',(w,h)); d=ImageDraw.Draw(bg)
    for y in range(h):
        k=y/max(1,h-1); rgb=tuple(int(colors[0][j]*(1-k)+colors[1][j]*k) for j in range(3))
        d.line((0,y,w,y),fill=rgb)
    d.ellipse((int(w*.1),int(h*.17),int(w*.9),int(h*.8)),outline=(70,165,190),width=max(2,w//120))
    scale=(.62+.09*math.sin(progress*math.pi)) if shot!=5 else .7+.03*progress
    if shot==0: scale=.38+.3*progress
    maxw=int(w*scale); maxh=int(h*.53)
    ratio=min(maxw/product.width,maxh/product.height)
    img=product.resize((max(1,int(product.width*ratio)),max(1,int(product.height*ratio))),Image.Resampling.LANCZOS)
    x=(w-img.width)//2+int(math.sin(progress*math.pi*2)*w*.025)
    y=int(h*.43-img.height/2)+int(math.sin(progress*math.pi)*h*.015)
    if img.mode=='RGBA': bg.paste(img,(x,y),img)
    else: bg.paste(img,(x,y))
    d=ImageDraw.Draw(bg)
    label=p['shots'][shot]['name'].upper()
    bbox=d.textbbox((0,0),label,font=font(max(14,w//16))); tw=bbox[2]-bbox[0]
    d.text(((w-tw)//2,int(h*.81)),label,font=font(max(14,w//16)),fill='white')
    if shot==5:
        subtitle='MADE TO STAND OUT'
        bbox=d.textbbox((0,0),subtitle,font=font(max(11,w//32))); tw=bbox[2]-bbox[0]
        d.text(((w-tw)//2,int(h*.88)),subtitle,font=font(max(11,w//32)),fill=(210,238,245))
    return bg

def render(product_path: str, prompt: str, output: str, duration=30, style='cinematic', width=360, height=640, fps=12):
    if not shutil.which('ffmpeg'): raise RuntimeError('ffmpeg not found. Install ffmpeg first.')
    if not (64<=width<=1920 and 64<=height<=1920 and 1<=fps<=60): raise ValueError('invalid resolution or FPS')
    src=Path(product_path)
    if not src.is_file(): raise FileNotFoundError(src)
    with Image.open(src) as source:
        product=ImageOps.exif_transpose(source).convert('RGBA')
    p=plan(str(src),prompt,duration,style)
    dest=Path(output).resolve(); dest.parent.mkdir(parents=True,exist_ok=True)
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{width}x{height}', '-framerate',str(fps),'-i','pipe:0','-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(duration*fps):
            proc.stdin.write(frame(product,p,i/fps,width,height).tobytes())
        proc.stdin.close(); error=proc.stderr.read().decode(errors='replace'); code=proc.wait()
    except Exception:
        proc.kill();proc.wait();raise
    if code: raise RuntimeError('ffmpeg failed: '+error[-2000:])
    dest.with_suffix('.json').write_text(json.dumps(p,indent=2))
    return dest
