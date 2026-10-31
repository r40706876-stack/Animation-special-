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
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(text)
    print(text)
if __name__=='__main__':main()
