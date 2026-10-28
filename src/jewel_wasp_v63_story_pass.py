"""V6.3: visible sting insertion, tighter pursuit/antenna framing, burrow staging,
larva macro cleanup. Direct response to actual V6.2 proof 40782659283.
This is a non-rendering scene pass. V4 is never modified.
"""
import math
from mathutils import Vector

# A ground-level hole must be adjacent to the roach, not a separate black
# oval in the distance. Hide the old V6.2 aperture and make an uneven mouth.
if chapter >= 10:
    for obj in bpy.data.objects:
        if obj.name.startswith(("V6.2 visible dark burrow mouth", "V6.2 irregular low earth lip")):
            obj.hide_render = True
    hole_x, hole_y = (1.55, 1.85)
    hole_mat = organic_material("V6.3 cavity charcoal", (.001,.001,.001), (.012,.007,.004), 13,.99)
    ell("V6.3 burrow dark opening", (hole_x,hole_y,.055), (.69,.51,.022), hole_mat)
    for j in range(26):
        a = j*math.tau/26
        radx = .75+.07*math.sin(3*a)
        rady = .58+.04*math.sin(5*a)
        pebble=ell("V6.3 uneven burrow lip",
            (hole_x+radx*math.cos(a),hole_y+rady*math.sin(a),.095),
            (.10+.035*abs(math.sin(j)),.085,.048),soil)
        pebble.rotation_euler.z = a

# Explicit 3D needle, dynamically following the wasp and the roach. The old
# local gaster needle was buried under the wing and could not be seen.
if chapter in (3,5):
    for obj in bpy.data.objects:
        if obj.name.startswith(("V6.2 animated contact needle", "V4 visible sting needle", "sting tip")):
            obj.hide_render = True
    needle_mat=mat("V6.3 copper-brown ovipositor",(.12,.048,.018),.26,.37)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.024,radius2=.002,depth=1)
    shaft=bpy.context.object
    shaft.name="V6.3 visible articulated stinger"
    shaft.data.materials.append(needle_mat)
    mark_mat=mat("V6.3 tiny sting contact mark",(.23,.046,.018),.08,.65)
    mark=ell("V6.3 roach sting entry",(0,-.54 if chapter==3 else -.91,.66),
             (.07,.06,.012),mark_mat,roach)
    for frame,reach in ((1,.03),(84,.03),(93,.32),(102,.74),(110,1.0),(121,1.0),(138,.25),(160,.03),(240,.03)):
        scene.frame_set(frame)
        start=Vector(wasp.location)+(0,.40,.50)
        target=Vector(roach.location)+(0,-.54 if chapter==3 else -.91,.62)
        tip=start+(target-start)*reach
        direction=tip-start
        length=max(.002,direction.length)
        shaft.location=(start+tip)/2
        shaft.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
        shaft.scale=(1,1,length)
        for path in ('location','rotation_euler','scale'):
            shaft.keyframe_insert(data_path=path,frame=frame)
        mark.scale=(.07*reach,.06*reach,.012)
        mark.keyframe_insert(data_path='scale',frame=frame)
    scene.frame_set(120)

# Scene 12 should be a clean macro of larval growth, not disconnected black
# leg/antenna rods hanging over the larva.
if chapter==12:
    for obj in bpy.data.objects:
        if obj.name.startswith(("V6 femur","V6 tibia","V6 joint","cockroach antenna",
                                "V4 articulated roach antenna","cockroach leg upper",
                                "cockroach leg lower","V4 wing cover seam")):
            obj.hide_render=True
    for obj in bpy.data.objects:
        if obj.name.startswith("V6.1 growing larva segment"):
            for frame in (95,120,145,170,195,220):
                scene.frame_set(frame)
                obj.rotation_euler.y=.10*math.sin(frame*.085+obj.location.y*9)
                obj.keyframe_insert(data_path='rotation_euler',frame=frame)
    scene.frame_set(120)

# Separate the story grammar: pursuit, antenna control and burrow approach
# must not reuse nearly identical wide shots.
if chapter==1:
    pos,target,lens=(-2.7,-3.5,1.9),(-.45,-.62,.47),30
elif chapter==7:
    pos,target,lens=(-2.15,-2.65,1.55),(-.43,-.94,.48),31
elif chapter==10:
    pos,target,lens=(3.25,-2.8,2.45),(1.20,1.02,.29),27
elif chapter==13:
    pos,target,lens=(3.2,-3.1,2.8),(1.40,1.0,1.22),29

# Neural-impulse chapters intentionally remove the wasp. Later anatomy
# objects were created after the original hide pass, so hide all descendants.
if chapter in (4,6):
    for obj in bpy.data.objects:
        parent=obj
        while parent is not None:
            if parent==wasp:
                obj.hide_render=True
                break
            parent=parent.parent

# Restore scene to the proof frame after sampling animated object transforms.
scene.frame_set(120)
