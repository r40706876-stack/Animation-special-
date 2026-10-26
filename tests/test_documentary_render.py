"""Offline rendering smoke test: no API keys, no paid services."""
import pathlib, sys, tempfile
from PIL import Image
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/"src"))
import documentary as d
def main():
    with tempfile.TemporaryDirectory() as td:
        d.WORK=pathlib.Path(td)
        scene={"label":"जीव विज्ञान","fact":"प्रकृति का अनोखा रहस्य","motion":"zoom"}
        out=d.WORK/"smoke.mp4"
        d.render_scene(Image.new("RGB",(720,1280),(24,55,65)),scene,0,1.0,out)
        assert out.exists() and out.stat().st_size>1000
        assert abs(d.duration(out)-1.0)<0.25
        scan=d.WORK/"scan.mp4"
        d.render_scene(Image.new("RGB",(720,1280),(24,55,65)),scene,2,1.0,scan)
        assert scan.exists() and scan.stat().st_size>1000
        print("RENDER_SMOKE_PASS")
if __name__=="__main__":main()
