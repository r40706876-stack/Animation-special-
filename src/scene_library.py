"""Reusable underwater scenery for keyless Blender animation."""
import math
from animation_library import animate_rising_bubble

def populate_underwater(uv,floor_mat,bubble_mat,coral_mat):
    uv('Sea floor',(0,0,-.55),(9,9,.16),floor_mat)
    for i in range(22):
        a=i*2.39996
        r=2.4+(i%5)*.46
        bubble=uv('Bubble '+str(i),(r*math.cos(a),r*math.sin(a),.4+(i%9)*.29),(.035,.035,.055),bubble_mat)
        animate_rising_bubble(bubble,i)
    # Decorative reef clusters: all geometry is procedural and reusable.
    for cluster,x in enumerate((-2.85,2.85)):
        for i in range(7):
            height=.25+.14*(i%4)
            uv('Reef coral %d-%d'%(cluster,i),
               (x+.20*math.sin(i*1.7),1.3+.18*math.cos(i*1.5),-.34+height),
               (.12,.12,height),coral_mat)
