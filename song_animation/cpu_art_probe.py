"""One bounded, credential-free CPU artwork experiment; not a production backend.
Model documentation: https://huggingface.co/stabilityai/sd-turbo
"""
import json,time,os
from pathlib import Path

def main():
 out=Path('cpu_art_probe');out.mkdir(exist_ok=True);started=time.perf_counter()
 report={'available':False,'quality_certified':False,'model':'stabilityai/sd-turbo','device':'cpu','license_reference':'https://huggingface.co/stabilityai/sd-turbo','steps':2}
 try:
  import torch
  from diffusers import AutoPipelineForText2Image
  from huggingface_hub import model_info
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  revision=model_info(report['model']).sha;report['revision']=revision
  pipe=AutoPipelineForText2Image.from_pretrained(report['model'],revision=revision,variant='fp16',torch_dtype=torch.float32,use_safetensors=True,low_cpu_mem_usage=True)
  pipe.to('cpu');pipe.enable_attention_slicing('max')
  prompt='A premium botanical watercolor and finely engraved ink illustration of a single crimson rose in full bloom, organically curled layered petals, two olive leaves and short stem, isolated against plain cream handmade paper, rich petal depth and warm soft light, beautifully detailed, no words, no people.'
  image=pipe(prompt=prompt,num_inference_steps=2,guidance_scale=0.0,height=512,width=512,generator=torch.Generator(device='cpu').manual_seed(417)).images[0]
  image.save(out/'artwork.png');report.update(available=True,size=list(image.size),file='artwork.png',prompt=prompt)
 except Exception as e:
  report['error_type']=type(e).__name__;report['http_status']=getattr(getattr(e,'response',None),'status_code',None)
 finally:
  report['elapsed_seconds']=round(time.perf_counter()-started,2)
  (out/'capability.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
