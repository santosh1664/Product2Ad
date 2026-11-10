"""Optional MCP integration: pip install -e '.[mcp]'"""
from .core import plan,render

def main():
    try: from mcp.server.fastmcp import FastMCP
    except ImportError as exc: raise SystemExit("Install MCP support: pip install -e '.[mcp]'") from exc
    server=FastMCP('Product2Ad')
    @server.tool()
    def create_ad_plan(image_path: str, prompt: str, duration: int=30, style: str='cinematic') -> dict:
        """Plan an original product advertisement from a local image."""
        return plan(image_path,prompt,duration,style)
    @server.tool()
    def render_ad(image_path: str, prompt: str, output_path: str='outputs/ad.mp4',duration: int=30,style: str='cinematic') -> str:
        """Render a CPU motion-graphics MP4 and JSON storyboard; returns file path."""
        return str(render(image_path,prompt,output_path,duration,style))
    server.run(transport='stdio')
if __name__=='__main__': main()
