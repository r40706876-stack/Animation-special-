import copy,json,unittest
from pathlib import Path
from song_animation.choreography import retarget
from song_animation.vector import validate_vector,values
class ConnectedBody(unittest.TestCase):
    def test_walking_has_shared_root_and_alternating_attached_legs(self):
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        p['bible']={'characters':'a human poet'}
        p['scenes'][0]['action']='the person walks across the path'
        for name,w,h,shape in [('person_torso',100,150,'<rect width="100" height="150" fill="#a65b35"/>'),('person_head',65,85,'<ellipse cx="32" cy="42" rx="30" ry="40" fill="#dfb28b"/>')]:
            p['assets'][name]={'width':w,'height':h,'svg':f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{shape}</svg>'}
        original=copy.deepcopy(p);fixed,changed=retarget(p,0,['missing walking person'])
        self.assertTrue(changed);validate_vector(fixed)
        nodes={n['id']:n for n in fixed['scenes'][0]['nodes']}
        self.assertEqual(nodes['connected_0_left_leg']['parent'],'connected_0_root')
        self.assertEqual(nodes['connected_0_left_foot']['parent'],'connected_0_left_leg')
        self.assertGreater(abs(values(nodes['connected_0_root'],.8)['x']-values(nodes['connected_0_root'],.1)['x']),100)
        self.assertAlmostEqual(values(nodes['connected_0_left_leg'],.1)['rotation'],-values(nodes['connected_0_right_leg'],.1)['rotation'])
        # Walking feet must remain above the two-line caption area in every pose.
        import numpy as np
        from song_animation.vector import basis
        for t in (0,.1,.25,.5,.75,.9,1):
            matrices={}
            for n in fixed['scenes'][0]['nodes']:
                m=basis(values(n,t))
                if n.get('parent'):m=matrices[n['parent']]@m
                matrices[n['id']]=m
                if n['id'].endswith('_foot'):
                    a=fixed['assets'][n['asset']];w,h=a['width'],a['height'];px,py=n['pivot']
                    corners=m@np.array([[-px*w,(1-px)*w,(1-px)*w,-px*w],[-py*h,-py*h,(1-py)*h,(1-py)*h],[1,1,1,1]])
                    self.assertLessEqual(corners[1].max(),720)
        self.assertEqual(p,original)
    def test_nonhuman_world_is_not_replaced_by_a_person(self):
        p={'bible':{'characters':'a mechanical bird'},'scenes':[{'action':'walking'}],'assets':{}}
        same,changed=retarget(p,0,['walking parts missing'])
        self.assertFalse(changed);self.assertIs(same,p)
