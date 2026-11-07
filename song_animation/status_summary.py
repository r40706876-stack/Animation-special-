"""Show actual song status separately from code-only green checks in Actions."""
import argparse,json,os
from pathlib import Path

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',required=True);args=a.parse_args()
    p=Path(args.out)/'status.json'
    state=json.loads(p.read_text()) if p.is_file() else {'status':'not_started'}
    labels={'checks_passed':'वीडियो की स्वचालित जाँच पास हुई; यह मानव की स्वीकृति नहीं है।',
        'planned':'Lyrics और कहानी तैयार हैं; वीडियो का render अभी पूरा नहीं हुआ।',
        'waiting_for_provider':'वीडियो पूरा नहीं हुआ। मॉडल की quota/service availability खुलने पर retry चाहिए।',
        'blocked':'वीडियो की जाँच पास नहीं हुई; केवल review draft उपलब्ध हो सकता है।',
        'failed':'वीडियो निर्माण में त्रुटि आई।', 'not_started':'वीडियो निर्माण शुरू नहीं हुआ।'}
    text='## Song production\n\n'+labels.get(state.get('status'),'वीडियो अभी तैयार नहीं है।')+'\n\nStatus: `'+state.get('status','unknown')+'`\n'
    if state.get('automatic_repair_pending') is True:text+='\nबची हुई visual गलतियाँ और frames सुरक्षित हैं। अगली automatic कोशिश उन्हीं पर नया repair करेगी; अभी final MP4 तैयार नहीं है।\n'
    if state.get('reasons'):
        text+='\n### वीडियो क्यों रुका\n\n'+''.join('- '+str(r)[:600]+'\n' for r in state['reasons'][:30])
    image_hold=Path(args.out)/'image_provider_hold.json'
    if image_hold.is_file():
        try:text+='\n### चित्र सेवा का जवाब\n\n- '+str(json.loads(image_hold.read_text()).get('reason',''))[:600]+'\n'
        except ValueError:pass
    hold=Path(args.out)/'audio_hold.json'
    if hold.is_file():
        try:reasons=json.loads(hold.read_text()).get('reasons',[])
        except ValueError:reasons=[]
        text+='\n### गाने के बोल क्यों reject हुए\n\n'+''.join('- '+str(r)[:900]+'\n' for r in reasons)
    for f in sorted(Path(args.out).glob('*_response.txt'))[:8]:
        text+='\n<details><summary>'+f.name+'</summary>\n\n```\n'+f.read_text(errors='replace')[:(8000 if 'review' in f.name else 1500)]+'\n```\n</details>\n'
    ready=os.getenv('SONG_CHECKED_ARTIFACT_URL','')
    if state.get('status')=='checks_passed' and (Path(args.out)/'checked.mp4').is_file() and ready.startswith('https://github.com/'):
        text+='\n[तैयार वीडियो और lyrics डाउनलोड करें]('+ready+') — ZIP में checked.mp4 और lyrics.srt हैं।\n'
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(text)
    print(text)
if __name__=='__main__':main()
