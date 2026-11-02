import copy,unittest
import numpy as np
from song_animation.attachments import image_matrix,validate_attachment
from song_animation.vector import basis

class AttachedLimb(unittest.TestCase):
    def test_both_joints_remain_exact_under_a_moving_rotating_scaled_body(self):
        asset={'width':540,'height':270};body={'width':340,'height':480};parent={'id':'body','asset':'body','pivot':[.5,.5]};node={'id':'arm','asset':'arm','pivot':[.5,.5]}
        b={'parent':'body','parent_anchor':[.18,.43],'proximal':[.95,.68],'distal':[.22,.64],'thickness_scale':.52}
        validate_attachment(b,node,{'body':parent},{'arm':asset,'body':body})
        for x,y,angle,scale in [(420,500,-1,.96),(390,480,17,1.2),(370,485,.5,1)]:
            pm=basis({'x':x,'y':y,'rotation':angle,'scale':scale});tm=basis({'x':175,'y':435,'rotation':0,'scale':1})
            m=image_matrix(asset,node,b,body,parent,pm,tm)
            shoulder=(pm@np.array([(b['parent_anchor'][0]-.5)*340,(b['parent_anchor'][1]-.5)*480,1]))[:2]
            for name,expected in [('proximal',shoulder),('distal',[175,435])]:
                point=(np.array(b[name])-.5)*[540,270]
                np.testing.assert_allclose((m@np.r_[point,1])[:2],expected,atol=1e-8)
    def test_invalid_binding_is_rejected_before_rendering(self):
        node={'asset':'arm'};prior={'body':{'asset':'body'}}
        valid={'parent':'body','parent_anchor':[.2,.4],'proximal':[.9,.6],'distal':[.2,.6]}
        for field,value in [('parent','future'),('distal',[.9,.6]),('parent_anchor',[float('nan'),0]),('thickness_scale',0)]:
            b=copy.deepcopy(valid);b[field]=value
            with self.assertRaises(ValueError):validate_attachment(b,node,prior,{})
        b=copy.deepcopy(valid);b['distal']=b['proximal']
        with self.assertRaises(ValueError):validate_attachment(b,node,prior,{})
