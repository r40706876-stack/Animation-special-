"""Reusable procedural underwater environment for Blender renders."""
import math
import bpy
from mathutils import Vector
from animation_library import animate_rising_bubble

def _coral_branch(name, base, tip, bottom_radius, material):
    """Smooth tapered coral branch with real depth and a joined silhouette."""
    direction=Vector(tip)-Vector(base)
    midpoint=(Vector(base)+Vector(tip))/2
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=bottom_radius,
        radius2=bottom_radius*.46, depth=direction.length, location=midpoint)
    branch=bpy.context.object
    branch.name=name
    branch.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    branch.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return branch

def populate_underwater(uv, floor_mat, bubble_mat, coral_mat):
    """Add ocean floor, gently rising bubbles and branching reef silhouettes."""
    # A real horizontal seabed avoids the artificial curved horizon created
    # by a giant flattened UV sphere.
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.55))
    seabed=bpy.context.object
    seabed.name='Reusable flat seabed'
    seabed.data.materials.append(floor_mat)
    # Contrasting low-poly pebbles add depth without expensive assets.
    rock_mat=bpy.data.materials.new('Blue-gray reef stones')
    rock_mat.diffuse_color=(.15,.26,.31,1)
    rock_mat.use_nodes=True
    rock_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.15,.26,.31,1)
    for i in range(12):
        x=(-1.7 if i%2==0 else 1.7)+.20*math.sin(i*2.1)
        y=.6+(i%4)*.28
        uv('Seabed pebble '+str(i),(x,y,-.46),(.13+.025*(i%3),.10,.075),rock_mat)
    # Soft underwater fill light separates the character from the background.
    bpy.ops.object.light_add(type='AREA',location=(-4,2.5,5))
    fill=bpy.context.object
    fill.name='Reusable cool underwater fill'
    fill.data.energy=650
    fill.data.color=(.35,.75,1.0)
    fill.data.shape='DISK'
    fill.data.size=6
    for i in range(22):
        a=i*2.39996
        r=2.4+(i%5)*.46
        bubble=uv('Bubble '+str(i),(r*math.cos(a),r*math.sin(a),.4+(i%9)*.29),
                  (.035,.035,.055),bubble_mat)
        animate_rising_bubble(bubble,i)
    # Unlike disconnected oval decorations, each coral is a branching stem.
    for cluster,x in enumerate((-1.58,1.58)):
        for i in range(3):
            stem_x=x+(i-1)*.21
            base=(stem_x,1.05,-.37)
            top=(stem_x+(i-1)*.08,1.05,.23+.12*(i%2))
            _coral_branch('Coral trunk %d-%d'%(cluster,i),base,top,.095,coral_mat)
            for side in (-1,1):
                fork=(top[0]+side*(.18+.04*i),1.05,.45+.10*(i%2))
                _coral_branch('Coral fork %d-%d-%d'%(cluster,i,side),
                              (top[0],top[1],top[2]-.08),fork,.058,coral_mat)
