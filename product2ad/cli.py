import argparse, json
from .core import render,plan
from .blender_pipeline import render_blender
from .reference_analysis import analyze_reference
from .motion.browser import build_motion_html
from .motion.export import export_motion

def main():
    parser=argparse.ArgumentParser(prog='product2ad',description='Create an original product ad from an image and prompt')
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ('plan','render'):
        p=sub.add_parser(command)
        p.add_argument('--image',required=True)
        p.add_argument('--prompt',default='Premium cinematic product advertisement')
        p.add_argument('--duration',type=int,default=30)
        p.add_argument('--style',choices=['cinematic','fresh','bold'],default='cinematic')
        if command=='render':
            p.add_argument('--output',default='outputs/ad.mp4');p.add_argument('--width',type=int,default=360);p.add_argument('--height',type=int,default=640);p.add_argument('--fps',type=int,default=12)
    b=sub.add_parser('render-3d', help='Render a 3D can scene with Blender 4.x')
    b.add_argument('--image', required=True)
    b.add_argument('--output', default='outputs/hero.mp4')
    b.add_argument('--duration', type=int, default=5)
    b.add_argument('--fps', type=int, default=24)
    b.add_argument('--width', type=int, default=720)
    b.add_argument('--height', type=int, default=1280)
    b.add_argument('--samples', type=int, default=32)
    b.add_argument('--blender', default='blender')
    b.add_argument('--dry-run', action='store_true')
    r=sub.add_parser('analyze-reference', help='Extract shot boundaries and motion statistics from an authorized reference video')
    r.add_argument('--video', required=True)
    r.add_argument('--output', default='outputs/reference-analysis.json')
    r.add_argument('--sample-fps', type=float, default=2.0)
    m=sub.add_parser('render-motion', help='Generate a continuous browser-motion ad (Bang Motion-inspired)')
    m.add_argument('--image', required=True)
    m.add_argument('--output', default='outputs/motion.html')
    m.add_argument('--prompt', default='Cinematic product reveal')
    m.add_argument('--duration', type=float, default=7)
    m.add_argument('--width', type=int, default=540)
    m.add_argument('--height', type=int, default=960)
    e=sub.add_parser('export-motion', help='Export deterministic browser motion HTML to H.264 MP4')
    e.add_argument('--html', required=True)
    e.add_argument('--output', default='outputs/motion.mp4')
    e.add_argument('--duration', type=float, default=7)
    e.add_argument('--fps', type=int, default=24)
    e.add_argument('--width', type=int, default=540)
    e.add_argument('--height', type=int, default=960)
    a=parser.parse_args()
    try:
        if a.command=='analyze-reference': print(json.dumps(analyze_reference(a.video, a.output, a.sample_fps), indent=2))
        elif a.command=='export-motion': print(json.dumps(export_motion(a.html,a.output,duration=a.duration,fps=a.fps,width=a.width,height=a.height),indent=2))
        elif a.command=='render-motion': print('HTML:', build_motion_html(a.image,a.output,a.prompt,a.duration,a.width,a.height))
        elif a.command=='plan': print(json.dumps(plan(a.image,a.prompt,a.duration,a.style),indent=2))
        elif a.command=='render-3d':
            print('Output:', render_blender(a.image,a.output,blender=a.blender,duration=a.duration,fps=a.fps,width=a.width,height=a.height,samples=a.samples,dry_run=a.dry_run))
        else: print('Video:',render(a.image,a.prompt,a.output,a.duration,a.style,a.width,a.height,a.fps))
    except (ValueError,FileNotFoundError,RuntimeError) as exc: parser.error(str(exc))

if __name__=='__main__':main()
