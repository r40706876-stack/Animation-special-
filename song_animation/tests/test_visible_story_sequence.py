import copy,tempfile,subprocess,unittest
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from song_animation.variety import measure
from song_animation.quality import visual_decision,CHECKS
from song_animation.tests.test_quality_gate import clear_review

def picture(kind=0):
    im=Image.new('RGB',(180,320),'#f6ead0');d=ImageDraw.Draw(im)
    if kind==0:
        d.rectangle((15,20,160,180),fill='#396785');d.line((90,20,90,180),fill='white',width=7)
        d.line((15,100,160,100),fill='white',width=7);d.polygon([(0,218),(180,190),(180,280),(0,280)],fill='#935b3a')
    elif kind==1:
        d.polygon([(0,20),(75,75),(30,130),(140,160),(80,260),(180,260),(180,0)],fill='#228a83')
        d.ellipse((8,155,60,235),fill='#b84a63');d.line((34,230,34,270),fill='#465c35',width=8)
    else:
        d.rectangle((7,130,173,270),fill='#d78d57');d.polygon([(0,130),(90,18),(180,130)],fill='#873f51')
        d.rectangle((67,167,115,270),fill='#343b52');d.ellipse((8,35,65,92),fill='#e6b33b')
    return im

def timeline(n=5,seconds=6):return [{'start_frame':i*seconds*12,'end_frame':(i+1)*seconds*12} for i in range(n)]

class ActualVisibleSequence(unittest.TestCase):
    def test_real_encoded_caption_changes_cannot_disguise_one_repeated_picture(self):
        from song_animation.review import encoded_sample
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for i in range(5):
                im=picture();ImageDraw.Draw(im).rectangle((0,267,180,320),fill=['white','red','blue','green','black'][i]);im.save(root/(str(i)+'.png'))
            video=root/'repeated.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-framerate','1/6','-i',str(root/'%d.png'),'-t','30','-r','12','-c:v','libx264','-pix_fmt','yuv420p',str(video)],check=True)
            scenes=timeline();samples=[[encoded_sample(video,i*6+q*5.9) for q in (.1,.5,.9)] for i in range(5)]
            report=measure(samples,scenes,12)
            self.assertFalse(report['passed']);self.assertEqual(report['observed_groups'],1)
            # Even an all-positive AI assertion cannot overrule measured repeats.
            review=clear_review(5);review['visual_variety_measurement']=report
            self.assertFalse(visual_decision(review,5)['passed'])

    def test_small_zooms_and_colour_grading_do_not_create_story_setups(self):
        samples=[]
        for i in range(5):
            im=picture().crop((i*1.5,i*2,180-i*1.5,320-i*2)).resize((180,320))
            im=ImageOps.colorize(ImageOps.grayscale(im),['#183d51','#453951'][i%2],['#fff0d0','#e6efe9'][i%2])
            samples.append([im]*3)
        self.assertFalse(measure(samples,timeline(),12)['passed'])

    def test_connected_callback_can_return_to_a_setup_after_other_scenes(self):
        report=measure([[picture(i)]*3 for i in [0,1,2,0,1]],timeline(),12)
        self.assertTrue(report['passed']);self.assertEqual(report['observed_groups'],3)

    def test_long_unchanged_opening_is_held_even_with_a_varied_ending(self):
        report=measure([[picture(i)]*3 for i in [0,0,1,2,1]],timeline(),12)
        self.assertFalse(report['passed']);self.assertEqual(report['max_same_setup_seconds'],12)
        self.assertIn(1,report['repair_shots'])

    def test_two_second_clip_is_not_forced_into_a_rapid_montage(self):
        self.assertTrue(measure([[picture()]*3],timeline(1,2),12)['passed'])

    def test_five_named_shots_cannot_replace_decoded_frame_evidence(self):
        r=clear_review(5);r.pop('visual_variety_measurement')
        self.assertFalse(visual_decision(r,5)['passed'])

    def test_model_cannot_replace_measured_repetition_with_its_own_positive_claim(self):
        from unittest.mock import patch
        from song_animation.review import review
        plan={'fps':12,'scenes':[dict(s,label='Synthetic shot') for s in timeline()],'lyrics':[],'story':{},'bible':{}}
        with tempfile.TemporaryDirectory() as td,patch('song_animation.review.encoded_sample',return_value=picture().resize((540,960))),patch('song_animation.review.generate_json',return_value=dict(clear_review(5),_provider_model='gemini-quality-pro')):
            result=review(plan,td)
        self.assertFalse(result['visual_variety_measurement']['passed'])
        self.assertFalse(visual_decision(result,5)['passed'])

    def test_pretty_varied_images_cannot_clear_a_song_unrelated_story(self):
        r=clear_review(5);r['lyric_story_connection']=False
        self.assertFalse(visual_decision(r,5)['passed'])

class StoryFaultMatrix(unittest.TestCase):
    def test_every_shot_and_every_required_check_rejects_missing_false_or_fake_booleans(self):
        cases=0
        for count in (1,3,5,8,12):
            for shot in range(count):
                for field in CHECKS:
                    for bad in (False,None,'true',1,'missing'):
                        with self.subTest(count=count,shot=shot,field=field,bad=bad):
                            r=clear_review(count)
                            if bad=='missing':r['shots'][shot].pop(field)
                            else:r['shots'][shot][field]=bad
                            self.assertFalse(visual_decision(r,count)['passed']);cases+=1
        self.assertEqual(cases,870)

    def test_every_cross_shot_story_link_requires_causality_continuity_and_progress(self):
        cases=0
        for count in (3,5,8,12):
            for link in range(count-1):
                for field in ('causal_connection','state_continuity','emotional_progression'):
                    for bad in (False,None,'true',1,'missing'):
                        with self.subTest(count=count,link=link,field=field,bad=bad):
                            r=clear_review(count)
                            if bad=='missing':r['story_links'][link].pop(field)
                            else:r['story_links'][link][field]=bad
                            self.assertFalse(visual_decision(r,count)['passed']);cases+=1
        self.assertEqual(cases,360)

    def test_wrong_missing_or_duplicate_shot_indices_never_clear(self):
        for bad in (True,-1,100,'0',None):
            with self.subTest(index=bad):
                r=clear_review(5);r['shots'][0]['shot']=bad
                self.assertFalse(visual_decision(r,5)['passed'])
        r=clear_review(5);r['shots'][1]['shot']=0
        self.assertFalse(visual_decision(r,5)['passed'])
