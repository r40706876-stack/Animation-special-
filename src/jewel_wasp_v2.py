"""Visual V2: forest floor detail, anatomical cues and insect locomotion.
This builds on the proven V1 rigs without modifying or deleting its finished film.
"""
import bpy, math, random, runpy, pathlib
from mathutils import Vector
_base = runpy.run_path(str(pathlib.Path(__file__).with_name("jewel_wasp_3d.py")))
for _name in ("scene","roach","wasp","cam","ell","mat","aim","link","soil","roachmat","wingmat","green","blue","trans","black","leaf","stone","leafgold","twigmat"):
    globals()[_name] = _base[_name]

def recolor(material, rgb, rough=.5, metal=0):
    material.diffuse_color=(*rgb,1)
    p=material.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*rgb,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal

recolor(roachmat,(.17,.056,.022),.49,.08)
recolor(wingmat,(.28,.095,.035),.39,.12)
recolor(green,(.012,.36,.16),.23,.69)
recolor(blue,(.009,.15,.31),.27,.62)
recolor(trans,(.18,.59,.50),.32,.06)
recolor(leaf,(.06,.17,.047),.92)
recolor(leafgold,(.29,.17,.058),.95)
recolor(soil,(.078,.064,.037),.96)
# Soil color variation from existing microtexture; avoid an unbroken beige floor.
bsdf=soil.node_tree.nodes.get("Principled BSDF")
noise=soil.node_tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=3.7
noise.inputs["Detail"].default_value=3.0
ramp=soil.node_tree.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.20
ramp.color_ramp.elements[0].color=(.035,.046,.025,1)
ramp.color_ramp.elements[1].position=.80
ramp.color_ramp.elements[1].color=(.15,.115,.062,1)
soil.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
soil.node_tree.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
# Combined meshes keep the richer forest inexpensive to render.
def scattered_quads(name,seed,count,materials,mode):
    rng=random.Random(seed)
    verts=[];faces=[];ids=[]
    for i in range(count):
        x=rng.uniform(-6,6);y=rng.uniform(-6,5)
        if abs(x)<.9 and -1.9<y<1.4 and mode!="moss":
            continue
        a=rng.random()*math.tau
        ca,sa=math.cos(a),math.sin(a)
        def v(dx,dy,z):
            verts.append((x+dx*ca-dy*sa,y+dx*sa+dy*ca,z))
            return len(verts)-1
        if mode=="leaves":
            length=rng.uniform(.13,.38);width=length*rng.uniform(.22,.43)
            z=.038+rng.random()*.018
            f=(v(-length,0,z),v(0,-width,z+.024),v(length,0,z),v(0,width,z+.024))
            faces.append(f);ids.append(i%len(materials))
        else:
            # Tiny upright grass/moss blades in loose patches.
            for j in range(3):
                theta=a+j*2.094
                dx=math.cos(theta)*.09;dy=math.sin(theta)*.09
                f=(v(-.025,0,.05),v(.025,0,.05),v(dx,dy,.11+rng.random()*.17))
                faces.append(f);ids.append(i%len(materials))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    for material in materials: mesh.materials.append(material)
    for poly,mi in zip(mesh.polygons,ids):poly.material_index=mi
    return obj

moss=mat("deep moss",(.037,.14,.045),0,.96)
moss2=mat("fern olive",(.085,.22,.07),0,.91)
dried=mat("dried leaves",(.34,.23,.085),0,.94)
scattered_quads("FOREST layered leaf litter",52,470,[leaf,leafgold,dried,moss2],"leaves")
scattered_quads("FOREST moss and sprouts",82,250,[moss,moss2],"moss")
# Fern fans around the action corridor: use low-poly combined fronds.
def ferns():
    rng=random.Random(173);vs=[];fs=[]
    for i in range(36):
        x=rng.uniform(-5.4,5.4);y=rng.uniform(-5,4.5)
        if abs(x)<1.6 and -2.4<y<1.4:continue
        a=rng.uniform(0,math.tau);h=rng.uniform(.25,.6)
        for k in range(4):
            aa=a+k*.65
            dx,dy=math.cos(aa),math.sin(aa)
            for j in range(3):
                d=.13+j*.13;w=.09*(1-j*.15)
                z=.055+h*(j+1)/4
                origin=len(vs)
                vs.extend([(x+dx*(d-.09)-dy*w,y+dy*(d-.09)+dx*w,z-.06),
                           (x+dx*(d+.12),y+dy*(d+.12),z+.06),
                           (x+dx*(d-.09)+dy*w,y+dy*(d-.09)-dx*w,z-.06)])
                fs.append((origin,origin+1,origin+2))
    mesh=bpy.data.meshes.new("fern fronds");mesh.from_pydata(vs,[],fs);mesh.update()
    obj=bpy.data.objects.new("FOREST ferns",mesh);scene.collection.objects.link(obj)
    mesh.materials.append(moss2)
ferns()
# Branches, bark and roots add foreground depth without obscuring the action.
bark=mat("forest bark",(.11,.066,.029),0,.94)
for i in range(30):
    a=i*2.399;x=-5.0+(i*17%101)/10;y=-4.5+(i*23%91)/10
    if abs(x)<1.6 and -2.2<y<1.5:continue
    link("forest branch %02d"%i,(x,y,.075),(x+.38*math.cos(a),y+.32*math.sin(a),.10),.025,bark,None)
# Rebuild highlights and details so insects read as arthropods, not plain spheres.
for obj in bpy.data.objects:
    if obj.name.startswith("cockroach eye"):obj.scale*=.83
    if obj.name.startswith("wasp eye"):obj.scale*=.82
    if obj.name.startswith("wasp head"):obj.scale*=.82
    if obj.name.startswith("wasp abdomen"):obj.scale.x*=.88
    if obj.name.startswith("animated wasp wing"):
        obj.scale.x*=.75;obj.scale.y*=.76;obj.scale.z*=.72
# Transparent wings with a dark leading vein.
p=trans.node_tree.nodes.get("Principled BSDF")
p.inputs["Alpha"].default_value=.58
if hasattr(trans,"surface_render_method"):
    trans.surface_render_method="DITHERED"
for side in (-1,1):
    for i in range(4):
        y=.30+i*.18
        ell("roach dorsal tergite %d %d"%(side,i),(side*.30,y,.41),(.055,.075,.09),wingmat,roach)
    # Curved, tapering antennae rather than straight sticks.
    points=[(side*.12,-1.12,.41),(side*.22,-1.48,.44),(side*.34,-1.82,.46),(side*.48,-2.16,.42),(side*.63,-2.48,.32)]
    for i in range(len(points)-1):
        link("segmented roach antenna %d %d"%(side,i),points[i],points[i+1],.008,black,roach)
    for i in range(2):
        y=-.42+i*.32
        ell("wasp coxa %d %d"%(side,i),(side*.18,y,.27),(.058,.08,.07),blue,wasp)
    points=[(side*.09,-.57,.41),(side*.18,-.78,.43),(side*.26,-.97,.39),(side*.32,-1.10,.31)]
    for i in range(len(points)-1):
        link("segmented wasp antenna %d %d"%(side,i),points[i],points[i+1],.008,black,wasp)
ell("wasp waist",(0,.14,.35),(.09,.20,.08),blue,wasp)
ell("wasp thorax shield",(0,-.14,.54),(.18,.20,.045),green,wasp)
ell("roach pronotum",(0,-.68,.54),(.32,.28,.075),wingmat,roach)
# Animated leg swings with alternating tripod gait, looping in the full film.
for insect in (roach,wasp):
    legs=[o for o in bpy.data.objects if o.parent==insect and ("leg" in o.name.lower())]
    for idx,obj in enumerate(legs):
        base_angle=obj.rotation_euler.z
        for frame in (1,7,13,19,25):
            obj.rotation_euler.z=base_angle+(.14 if insect==roach else .10)*math.sin((frame-1)*math.tau/24+idx*math.pi)
            obj.keyframe_insert(data_path="rotation_euler",frame=frame)
# A second, soft rim light makes the insect silhouettes distinguishable.
bpy.ops.object.light_add(type="AREA",location=(-3,1.0,4.2))
bpy.context.object.data.energy=520
bpy.context.object.data.size=4.5
print("JEWEL_V2_FOREST_RIG_READY",len(bpy.data.objects),flush=True)
