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
    uv('Sea floor',(0,0,-.55),(9,9,.16),floor_mat)
    for i in range(22):
        a=i*2.39996
        r=2.4+(i%5)*.46
        bubble=uv('Bubble '+str(i),(r*math.cos(a),r*math.sin(a),.4+(i%9)*.29),
                  (.035,.035,.055),bubble_mat)
        animate_rising_bubble(bubble,i)
    # Unlike disconnected oval decorations, each coral is a branching stem.
    for cluster,x in enumerate((-2.65,2.65)):
        for i in range(3):
            stem_x=x+(i-1)*.21
            base=(stem_x,.65,-.37)
            top=(stem_x+(i-1)*.08,.65,.23+.12*(i%2))
            _coral_branch('Coral trunk %d-%d'%(cluster,i),base,top,.095,coral_mat)
            for side in (-1,1):
                fork=(top[0]+side*(.18+.04*i),.65,.45+.10*(i%2))
                _coral_branch('Coral fork %d-%d-%d'%(cluster,i,side),
                              (top[0],top[1],top[2]-.08),fork,.058,coral_mat)
