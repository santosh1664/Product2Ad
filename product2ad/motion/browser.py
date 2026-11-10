"""Standalone, deterministic browser-motion renderer (not copied from Bang Motion)."""
import base64
import html
import json
from pathlib import Path


def build_motion_html(image, output, prompt='Cinematic product reveal', duration=7, width=540, height=960):
    source = Path(image).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise ValueError('Image must be PNG, JPG, JPEG or WebP')
    if not 2 <= duration <= 120:
        raise ValueError('Duration must be between 2 and 120 seconds')
    if not (240 <= width <= 1920 and 240 <= height <= 1920):
        raise ValueError('Invalid dimensions')
    mime = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}[source.suffix.lower()]
    uri = 'data:'+mime+';base64,'+base64.b64encode(source.read_bytes()).decode('ascii')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # A persistent stage, a motivated camera, and time-addressable deterministic animation.
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Product2Ad Motion</title>
<style>*{box-sizing:border-box}html,body{margin:0;background:#08080d;overflow:hidden}#stage{width:100vw;height:100vh;position:relative;overflow:hidden;background:radial-gradient(ellipse at 65% 38%,#b92534 0%,#440c1a 39%,#08080d 78%);font-family:Arial,Helvetica,sans-serif;color:white}#world{position:absolute;inset:0;transform-style:preserve-3d;will-change:transform}.halo{position:absolute;width:100%;aspect-ratio:1;top:10%;left:0;border-radius:50%;background:radial-gradient(circle,#ff425955 0%,#f12a3822 35%,transparent 70%);filter:blur(20px)}.ring{position:absolute;width:85%;aspect-ratio:1;border:2px solid #ffffff3b;border-radius:50%;left:7.5%;top:22%;box-shadow:0 0 40px #f15c6577;transform:rotateX(65deg)}.can{position:absolute;top:14%;left:15%;width:70%;height:68%;object-fit:contain;filter:drop-shadow(22px 36px 24px #000b);will-change:transform}.can.echo{opacity:.34;filter:blur(2px) drop-shadow(15px 25px 18px #0008)}#light{position:absolute;inset:-50%;background:linear-gradient(105deg,transparent 43%,#ffffff00 48%,#ffffff40 50%,#ffffff00 52%,transparent 58%);mix-blend-mode:screen;pointer-events:none}#headline{position:absolute;top:8%;width:100%;text-align:center;font-size:clamp(22px,6vw,72px);font-weight:900;letter-spacing:.16em;text-transform:uppercase;text-shadow:0 3px 25px #0009}#tag{position:absolute;bottom:10%;width:100%;text-align:center;font-size:clamp(14px,2.6vw,32px);letter-spacing:.28em;text-transform:uppercase}#scrub{display:none;position:absolute;bottom:0;width:100%;background:#0009;padding:10px}body.debug #scrub{display:block}#scrub input{width:90%}</style></head><body><div id="stage"><div id="world"><div class="halo"></div><div class="ring" id="ring"></div><img class="can echo" id="echo" src="__URI__"><img class="can" id="can" src="__URI__"><div id="light"></div></div><div id="headline">THE REVEAL</div><div id="tag">A MOMENT IN MOTION</div></div><div id="scrub"><input type="range" id="seek" min="0" max="__DURATION__" step="0.01"></div>
<script>const D=__DURATION__, world=document.getElementById('world'),can=document.getElementById('can'),echo=document.getElementById('echo'),ring=document.getElementById('ring'),light=document.getElementById('light'),headline=document.getElementById('headline'),tag=document.getElementById('tag');let start=performance.now();const clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),ease=x=>x*x*(3-2*x);function render(t){t=clamp(t,0,D);const p=t/D;const intro=ease(clamp(p/.26,0,1)),outro=ease(clamp((p-.73)/.27,0,1));world.style.transform=`perspective(900px) translate3d(${Math.sin(p*6.28)*2}%,${-intro*2+outro*3}%,0) scale(${1.07+intro*.10-outro*.08})`;can.style.transform=`translate3d(${Math.sin(p*5.7)*9}%,${Math.cos(p*5.2)*2}%,0) rotate(${Math.sin(p*5.2)*8}deg) scale(${.80+intro*.25-outro*.06})`;echo.style.transform=`translate3d(${-30+Math.sin(p*4)*15}%,${Math.cos(p*3)*4}%,0) rotate(${-18+p*25}deg) scale(.78)`;ring.style.transform=`perspective(600px) rotateX(67deg) rotateZ(${p*115}deg) scale(${.8+intro*.3})`;light.style.transform=`translateX(${p*95-60}%)`;headline.style.opacity=String(1-ease(clamp((p-.15)/.2,0,1)));headline.style.transform=`translateY(${(1-intro)*-40}px)`;tag.style.opacity=String(ease(clamp((p-.6)/.2,0,1)));}window.renderAt=(t)=>{render(t);return true};window.product2adReady=true;function loop(){render((performance.now()-start)/1000%D);requestAnimationFrame(loop)}if(location.search.includes('debug')){document.body.classList.add('debug');document.getElementById('seek').oninput=e=>render(Number(e.target.value));}else{requestAnimationFrame(loop)}</script></body></html>'''
    document = document.replace('__URI__',uri).replace('__DURATION__',str(float(duration)))
    output.write_text(document, encoding='utf-8')
    return str(output)
