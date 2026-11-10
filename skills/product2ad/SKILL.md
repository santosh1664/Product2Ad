---
name: product2ad
description: Create a product advertisement from an authorized product image and natural-language prompt using Product2Ad tools.
---
# Product2Ad
When asked to make a product advertisement:
1. Confirm a local image path exists. Ask for the image if missing.
2. Interpret the requested duration (default 30 seconds), style and target format.
3. Call `create_ad_plan` using the Product2Ad MCP server or `product2ad plan`.
4. Inspect the storyboard; explain that v0.1 is CPU motion graphics, NOT generative cinematic footage.
5. Call `render_ad` or `product2ad render` with the chosen settings.
6. Verify the output exists and, if ffprobe is available, check duration.
7. Return the actual MP4 path and storyboard JSON. Offer to revise the style.
Never claim that a still image has been turned into photorealistic AI video. Do not claim a preview is embedded unless the host supports it. Use only images and music the user is authorized to use.

## Experimental 3D renderer

For a cylindrical can, prefer `product2ad render-3d --image INPUT --output
OUTPUT --duration 5` when Blender 4.x and FFmpeg are installed. First call
`product2ad render-3d --image INPUT --dry-run` to validate arguments. Do not
claim Blender renders have succeeded unless the MP4 exists and has been
inspected. This renderer approximates the back of the product and is not a
photorealistic 30-second AI video generator. If Blender is unavailable,
report that limitation rather than silently substituting the 2D renderer.
