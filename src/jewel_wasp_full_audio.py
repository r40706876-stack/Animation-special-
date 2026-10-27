"""Generate 14 independently timed Hindi narration chapters (10 seconds each).
Fails loudly if voice generation fails: ambient-only is NOT a complete documentary.
"""
import asyncio,subprocess,pathlib
import edge_tts
lines=[
"जंगल की ज़मीन पर एक कॉकरोच भोजन खोज रहा है। लेकिन पास ही एक चमकदार हरी ज्वेल वास्प उसकी हर हरकत देख रही है।",
"यह छोटी ततैया अपने से बड़े कॉकरोच के पीछे जाती है। उसके लिए यह शिकार सिर्फ भोजन नहीं, अगली पीढ़ी का सहारा है।",
"कॉकरोच तेज़ी से बचने की कोशिश करता है। ततैया सही मौके की प्रतीक्षा करती है, और उसके पास पहुँचकर खुद को स्थिर करती है।",
"पहला डंक छाती के तंत्रिका केंद्रों के पास लगता है। इससे कॉकरोच के अगले पैरों की गति कुछ समय के लिए प्रभावित होती है।",
"कॉकरोच तुरंत पूरी तरह लकवाग्रस्त नहीं होता। पहला डंक ततैया को अगली, कहीं अधिक सटीक कार्रवाई के लिए समय देता है।",
"अब ततैया दूसरा डंक सिर के अंदर मौजूद तंत्रिका केंद्रों के पास पहुँचाती है। यह उसके व्यवहार को बदलने वाली मुख्य घटना है।",
"ज़हर तंत्रिका संकेतों पर असर डालता है। यहाँ चमकते हुए बिंदु केवल वैज्ञानिक समझ के लिए बनाए गए सांकेतिक चित्र हैं।",
"कुछ देर बाद कॉकरोच चल तो सकता है, लेकिन सामान्य हालत की तरह खुद से भागने की कोशिश बहुत कम करता है।",
"ततैया अब कॉकरोच के एंटीना को पकड़ती है। वह उसे खींचकर नहीं घसीटती, बल्कि चलते हुए अपने पीछे आने के लिए निर्देशित करती है।",
"दोनों जंगल की ज़मीन से होकर एक छोटे बिल की ओर बढ़ते हैं। कॉकरोच के पैर चलते हैं, लेकिन भागने की प्रतिक्रिया बदली हुई है।",
"बिल के पास पहुँचकर ततैया कॉकरोच को भीतर ले जाती है। यह सुरक्षित जगह उसके विकसित होते बच्चे के लिए तैयार की गई है।",
"ततैया कॉकरोच के शरीर पर एक अंडा रखती है और बिल बंद कर देती है। इसके बाद उसके बच्चे का विकास शुरू होगा।",
"अंडे से निकला लार्वा कॉकरोच को भोजन के रूप में इस्तेमाल करता है। यह प्रकृति की जटिल परजीवी जीवन रणनीतियों में से एक है।",
"ज्वेल वास्प का यह व्यवहार दिखाता है कि कीड़ों की तंत्रिका प्रणाली कितनी विशिष्ट होती है। यह जादू नहीं, विकास और जीवविज्ञान है।"
]
async def make(i,s):
 for attempt in range(3):
  try:
   await edge_tts.Communicate(s,'hi-IN-SwaraNeural',rate='+17%').save(f'voice/{i:02d}.mp3')
   if pathlib.Path(f'voice/{i:02d}.mp3').stat().st_size>1000:return
  except Exception as exc:
   print('VOICE_RETRY',i,attempt,str(exc),flush=True)
   await asyncio.sleep(2+attempt*3)
 raise RuntimeError(f'Unable to generate chapter {i} Hindi narration')
async def main():
 pathlib.Path('voice').mkdir(exist_ok=True)
 for i,line in enumerate(lines):
  await make(i,line)
  subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'voice/{i:02d}.mp3','-af','apad','-t','10','-ar','44100','-ac','2','-c:a','aac',f'voice/{i:02d}.m4a'],check=True)
 with open('voice/concat.txt','w') as f:
  for i in range(len(lines)):f.write(f"file '{i:02d}.m4a'\\n")
 subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','voice/concat.txt','-t','140','-ar','44100','-ac','2','-c:a','aac','voice/narration.m4a'],check=True)
 print('JEWEL_FULL_HINDI_NARRATION_READY',len(lines),flush=True)
if __name__=='__main__':asyncio.run(main())
