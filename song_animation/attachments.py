"""Two-point image bindings: a limb stays joined while its hand reaches a target.

The node's x/y keys are the world-space distal target. Normalized source
anchors identify the proximal joint and distal joint in the asset image.
The parent anchor is normalized in the parent's actual asset rectangle.
"""
import math
import numpy as np


def validate_attachment(binding,node,prior,assets):
    if not isinstance(binding,dict):raise ValueError('Invalid limb attachment')
    parent=binding.get('parent')
    if parent not in prior or node.get('parent') or not node.get('asset'):
        raise ValueError('Limb attachment needs an earlier asset parent and a world-space target')
    if not prior[parent].get('asset'):raise ValueError('Limb attachment parent must have an asset')
    for key in ('parent_anchor','proximal','distal'):
        v=binding.get(key)
        if not isinstance(v,list) or len(v)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) or not 0<=x<=1 for x in v):
            raise ValueError('Invalid normalized limb anchor')
    if math.dist(binding['proximal'],binding['distal'])<.02:raise ValueError('Limb anchors must be distinct')
    thickness=binding.get('thickness_scale')
    if thickness is not None and (type(thickness) not in (int,float) or not math.isfinite(thickness) or not .05<=thickness<=4):
        raise ValueError('Invalid limb thickness')


def image_matrix(asset,node,binding,parent_asset,parent_node,parent_matrix,target_matrix):
    size=np.array([asset['width'],asset['height']],float)
    p=np.array(binding['proximal'])*size;q=np.array(binding['distal'])*size
    parent_size=np.array([parent_asset['width'],parent_asset['height']],float)
    anchor=(np.array(binding['parent_anchor'])-np.array(parent_node.get('pivot',[.5,.5])))*parent_size
    shoulder=(parent_matrix@np.r_[anchor,1])[:2]
    target=target_matrix[:2,2];direction=target-shoulder;distance=np.linalg.norm(direction)
    if distance<1:raise ValueError('Limb target overlaps its proximal joint')
    source=q-p;length=np.linalg.norm(source)
    if length<1:raise ValueError('Degenerate limb source anchors')
    u=source/length;v=direction/distance
    source_axes=np.column_stack((u,[-u[1],u[0]]));target_axes=np.column_stack((v,[-v[1],v[0]]))
    along=distance/length;across=binding.get('thickness_scale',along)
    linear=target_axes@np.diag([along,across])@source_axes.T
    result=np.eye(3);result[:2,:2]=linear
    # paste() subtracts the ordinary pivot; compensate here so image anchors
    # refer to the real raster rather than to its node pivot convention.
    pivot=np.array(node.get('pivot',[.5,.5]))*size
    result[:2,2]=shoulder-linear@p+linear@pivot
    return result
