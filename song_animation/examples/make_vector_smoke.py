"""Original synthetic scene-graph proof, not real-song or genre certification."""
import json
from pathlib import Path

def svg(body,vb='0 0 160 200'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>'
def asset(body,w=160,h=200,vb='0 0 160 200'):return {'svg':svg(body,vb),'width':w,'height':h}
def node(id,aid,x,y,dx=0,dy=0,rotation=0,role='foreground',wave=None):
    n={'id':id,'asset':aid,'role':role,'pivot':[.5,.5],'keys':[{'t':0,'x':x,'y':y,'rotation':-rotation},{'t':1,'x':x+dx,'y':y+dy,'rotation':rotation}]}
    if wave:n['wave']=wave
    return n

def make():
    assets={
      'mountains':asset('<rect width="540" height="960" fill="#e8f0dd"/><circle cx="430" cy="170" r="65" fill="#edbe70"/><path d="M0 630L145 250L300 630Z" fill="#5e9992"/><path d="M180 640L360 300L540 640Z" fill="#88b2a2"/><path d="M0 640Q240 580 540 660V960H0Z" fill="#b9c9a0"/><path d="M140 960Q360 720 260 610" stroke="#f6e9c9" stroke-width="65" fill="none"/>',540,960,'0 0 540 960'),
      'kite':asset('<path d="M80 10L150 90L80 160L10 90Z" fill="#e76d61" stroke="#344d56" stroke-width="3"/><path d="M80 10V160M10 90H150" stroke="#fbecc5" stroke-width="3"/><path d="M80 160Q120 172 70 195" fill="none" stroke="#344d56" stroke-width="3"/>'),
      'cloud':asset('<path d="M15 95Q0 50 45 47Q58 4 90 30Q130 15 140 55Q180 80 145 100Z" fill="#fff9e7"/>',130,75,'0 0 165 110'),
      'temple':asset('<rect width="540" height="960" fill="#f7e6c8"/><circle cx="270" cy="260" r="155" fill="#f1cf89"/><path d="M90 610H450V960H90Z" fill="#ce8971"/><path d="M65 610L270 400L475 610Z" fill="#ae665f"/><path d="M165 960V705Q270 590 375 705V960Z" fill="#684d62"/><path d="M130 610V470L270 240L410 470V610Z" fill="#dbab74"/><path d="M145 470H395M180 400H360M215 330H325" stroke="#f8ddac" stroke-width="14"/><path d="M270 235V130L330 150L270 175" fill="#d3684d" stroke="#65485b" stroke-width="4"/>',540,960,'0 0 540 960'),
      'bell':asset('<path d="M80 20V50M25 140Q38 100 38 70Q80 35 122 70Q122 100 135 140Z" fill="#dfad51" stroke="#6d5360" stroke-width="4"/><ellipse cx="80" cy="140" rx="55" ry="12" fill="#b37a38"/><circle cx="80" cy="145" r="12" fill="#f7d888"/>'),
      'lamp':asset('<path d="M20 120Q80 170 140 120Z" fill="#b86755" stroke="#6d5360" stroke-width="3"/><path d="M80 119Q40 83 85 44Q115 80 80 119Z" fill="#e8a24a"/><path d="M80 112Q65 88 83 68Q96 95 80 112Z" fill="#fff3b2"/>'),
      'festival':asset('<rect width="540" height="960" fill="#f2e4d1"/><path d="M0 480Q270 330 540 480V960H0Z" fill="#94b5a5"/><path d="M0 170Q270 270 540 170" stroke="#6d5360" stroke-width="4" fill="none"/>'+''.join(f'<path d="M{x} 205L{x+35} 213L{x+13} 250Z" fill="{c}"/>' for x,c in zip(range(30,500,70),['#d77369','#e4bb59','#609fa0','#d77369','#e4bb59','#609fa0','#d77369'])),540,960,'0 0 540 960'),
      'drum':asset('<ellipse cx="80" cy="45" rx="62" ry="27" fill="#f5deb2" stroke="#665465" stroke-width="4"/><path d="M18 45L32 150Q80 185 128 150L142 45" fill="#cc7462" stroke="#665465" stroke-width="4"/><path d="M32 55L48 150L70 65L94 155L118 55" fill="none" stroke="#efd7a7" stroke-width="5"/><ellipse cx="80" cy="45" rx="62" ry="27" fill="#f5deb2" stroke="#665465" stroke-width="4"/>'),
      'stick':asset('<path d="M20 20L125 125" stroke="#665465" stroke-width="10" stroke-linecap="round"/>',100,100,'0 0 145 145')}
    scenes=[]
    for i,(label,bg,actors) in enumerate([
      ('Journey and a rising kite','mountains',[node('kite','kite',250,470,50,-100,9),node('cloud','cloud',100,230,140,0)]),
      ('Devotional lamp and swinging bell','temple',[node('bell','bell',270,350,0,0,16),node('lamp','lamp',270,665,wave={'rotation':6,'cycles':4})]),
      ('Festival drum rhythm','festival',[node('drum','drum',270,540,wave={'y':8,'cycles':4}),node('stick','stick',280,415,wave={'rotation':28,'cycles':4})])]):
        background=node('background',bg,270,480,role='background')
        scenes.append({'kind':'vector','label':label,'start_frame':i*96,'end_frame':(i+1)*96,'background':'#f8eedc','nodes':[background]+actors})
    return {'version':2,'title':'Synthetic scene-graph proof','fps':24,'total_frames':288,'assets':assets,'scenes':scenes,'lyrics':[]}
if __name__=='__main__':Path(__file__).with_name('vector_smoke.json').write_text(json.dumps(make(),indent=2))
