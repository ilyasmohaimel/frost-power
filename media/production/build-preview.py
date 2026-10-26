#!/usr/bin/env python3
"""Build and verify the full-length README animation using lossless BGRA encoding."""
import argparse,json,subprocess
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--input',type=Path,default=ROOT/'media/frost-power.mp4')
 p.add_argument('--output',type=Path,default=ROOT/'assets/frost-power-preview-lossless.webp')
 p.add_argument('--report',type=Path,default=ROOT/'media/work/preview-verification.json')
 p.add_argument('--width',type=int,default=800);p.add_argument('--fps',type=int,default=24)
 a=p.parse_args();height=round(a.width*9/16);height+=height%2
 filtering=f'fps={a.fps},scale={a.width}:{height}:flags=lanczos,format=bgra'
 common=['ffmpeg','-hide_banner','-loglevel','error','-i',str(a.input),'-vf',filtering,'-an']
 subprocess.run([*common,'-c:v','libwebp_anim','-pix_fmt','bgra','-lossless','1','-compression_level','6','-loop','0','-y',str(a.output)],check=True)
 # Check every decoded display frame against the exact scaled RGB input.
 # Container metadata alone did not catch the damaged older lossy animation.
 movie=subprocess.Popen([*common,'-f','rawvideo','-pix_fmt','bgra','-'],stdout=subprocess.PIPE)
 try:
  preview=Image.open(a.output);frame_index=0;start_ms=0;preview.seek(0);preview.load();end_ms=preview.info['duration'];count=0;maximum=0
  while data:=movie.stdout.read(a.width*height*4):
   assert len(data)==a.width*height*4,'Incomplete reference frame'
   midpoint=(count+.5)*1000/a.fps
   while midpoint>=end_ms and frame_index+1<preview.n_frames:
    frame_index+=1;start_ms=end_ms;preview.seek(frame_index);preview.load();end_ms+=preview.info['duration']
   expected=np.frombuffer(data,dtype=np.uint8).reshape(height,a.width,4)[:,:,[2,1,0]]
   actual=np.asarray(preview.convert('RGB'))
   maximum=max(maximum,int(np.abs(expected.astype(np.int16)-actual.astype(np.int16)).max()))
   count+=1
  assert movie.wait()==0,'Reference decode failed'
  assert count==20*a.fps and maximum==0,(count,maximum)
  while frame_index+1<preview.n_frames:
   frame_index+=1;preview.seek(frame_index);preview.load();end_ms+=preview.info['duration']
  assert abs(end_ms-20000)<100,end_ms
  report={'encoding':'lossless WebP, explicit BGRA input','width':a.width,'height':height,'fps':a.fps,'framesCompared':count,'maximumRgbError':maximum,'durationMs':end_ms,'encodedFrames':preview.n_frames,'bytes':a.output.stat().st_size,'comparison':'Every displayed preview frame equals its scaled MP4 reference pixels.'}
  a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 finally:
  if movie.poll() is None:movie.terminate();movie.wait()
if __name__=='__main__':main()
