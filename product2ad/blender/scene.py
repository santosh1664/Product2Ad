"""Executed by Blender 4.x (not normal Python): create an original 3D can spot.

Image is mapped as a front-facing product decal onto a cylinder. This is an
approximation, not a faithful 360-degree texture reconstruction.
"""
import bpy
import json
import math
import random
import sys
from pathlib import Path
from mathutils import Vector

job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = job['samples']
scene.render.resolution_x = job['width']
scene.render.resolution_y = job['height']
scene.render.resolution_percentage = 100
scene.render.fps = job['fps']
scene.frame_start = 1
scene.frame_end = job['duration'] * job['fps']
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(Path(job['output']).with_suffix('.frames') / 'frame_')
Path(scene.render.filepath).parent.mkdir(parents=True, exist_ok=True)
scene.world.color = (0.02, 0.03, 0.06)


def material(name, color, metallic=0.0, roughness=0.3):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

red = material('Enamel red', (0.65, 0.006, 0.012), 0.48, 0.22)
metal = material('Brushed aluminum', (0.72, 0.75, 0.79), 0.86, 0.22)
black = material('Studio floor', (0.008, 0.014, 0.025), 0.1, 0.25)

# Can body, rolled rims and a top lid; physical geometry and shadows.
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.84, depth=2.7, location=(0, 0, 1.65))
can = bpy.context.object
can.name = '3D Can Body'
can.data.materials.append(red)
bpy.ops.object.shade_smooth()
bev = can.modifiers.new('Soft rolled edges', 'BEVEL')
bev.width = 0.09
bev.segments = 4
can.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')

for z, radius, thickness in [(0.34, 0.78, 0.10), (2.98, 0.81, 0.09)]:
    bpy.ops.mesh.primitive_torus_add(major_segments=128, minor_segments=16,
                                     location=(0, 0, z), major_radius=radius, minor_radius=thickness)
    bpy.context.object.data.materials.append(metal)
    bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.79, depth=0.03, location=(0, 0, 3.01))
bpy.context.object.data.materials.append(metal)

# Product photo as a front-facing, curved decal mesh. The texture's white
# background is visible: source transparency or a clean crop works best.
mesh = bpy.data.meshes.new('Curved label mesh')
vertices, faces, uv = [], [], []
segments = 64
# Wrap the visible front half only, keeping the original logo legible.
for j in range(2):
    z = 0.52 if j == 0 else 2.83
    for i in range(segments + 1):
        theta = -1.34 + 2.68 * i / segments
        vertices.append((0.852 * math.sin(theta), -0.852 * math.cos(theta), z))
for i in range(segments):
    faces.append((i, i+1, segments+2+i, segments+1+i))
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new('Source image front decal', mesh)
scene.collection.objects.link(obj)
uvlayer = mesh.uv_layers.new()
for poly in mesh.polygons:
    i = poly.index
    for loop_idx, coord in zip(poly.loop_indices, [(i/segments, 0), ((i+1)/segments, 0), ((i+1)/segments, 1), (i/segments, 1)]):
        uvlayer.data[loop_idx].uv = coord
tex = bpy.data.materials.new('Source product image')
tex.use_nodes = True
nodes = tex.node_tree.nodes
bsdf = nodes.get('Principled BSDF')
image_node = nodes.new('ShaderNodeTexImage')
image_node.image = bpy.data.images.load(job['image'], check_existing=True)
tex.node_tree.links.new(image_node.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Metallic'].default_value = 0.35
bsdf.inputs['Roughness'].default_value = 0.26
obj.data.materials.append(tex)

# Procedural condensation droplets on the visible curved can surface.
# Mesh geometry catches studio highlights; deliberately non-fluid-simulated.
water = material('Condensation water', (0.78, 0.91, 1.0), 0.0, 0.07)
water.use_nodes = True
p = water.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 0.92
p.inputs['IOR'].default_value = 1.333
rng = random.Random(2026)
for i in range(110):
    theta = rng.uniform(-1.35, 1.35)
    z = rng.uniform(0.58, 2.75)
    r = rng.uniform(0.012, 0.038)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1,
        location=(0.857 * math.sin(theta), -0.857 * math.cos(theta), z))
    drop = bpy.context.object
    drop.name = 'Condensation %03d' % i
    drop.scale = (r, r * 0.48, r * rng.uniform(1.1, 2.1))
    drop.rotation_euler[2] = -theta
    drop.data.materials.append(water)
    bpy.ops.object.shade_smooth()

# Studio floor.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
bpy.context.object.data.materials.append(black)


def area(name, position, power, color, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = color
    data.shape = 'DISK'
    data.size = size
    o = bpy.data.objects.new(name, data)
    scene.collection.objects.link(o)
    o.location = position
    o.rotation_euler = (Vector((0, 0, 1.5)) - o.location).to_track_quat('-Z', 'Y').to_euler()

area('Large softbox', (3, -4, 6), 850, (0.74, 0.89, 1.0), 5)
area('Red rim light', (-3, 2, 4), 1150, (1.0, 0.08, 0.10), 3)
area('Cool edge light', (2, 3, 3), 1000, (0.1, 0.55, 1.0), 2)

camera_data = bpy.data.cameras.new('Camera')
camera = bpy.data.objects.new('Camera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'PERSP'
camera_data.lens = 47
for frame, position in [(1, (3.6, -7.8, 3.3)),
                        (scene.frame_end//2, (0.8, -6.6, 2.5)),
                        (scene.frame_end, (-2.3, -7.5, 3.0))]:
    camera.location = position
    camera.rotation_euler = (Vector((0, 0, 1.62)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.keyframe_insert(data_path='location', frame=frame)
    camera.keyframe_insert(data_path='rotation_euler', frame=frame)

scene.view_settings.view_transform = 'AgX'
bpy.ops.render.render(animation=True)
print('RENDER_COMPLETE', scene.render.filepath)
