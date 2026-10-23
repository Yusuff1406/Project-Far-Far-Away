#!/usr/bin/env python3
"""Execute Android's pure Java viewport sizing helper on the host JDK."""
import argparse,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--jdk',type=Path,required=True);a=ap.parse_args()
 cases=[(1920,1080,True,284),(2400,1080,True,356),(2520,1080,True,373),(1080,1920,True,240),(0,0,True,240),(3000,500,True,640),(2147483647,1,True,640),(1920,1080,False,240),(240,160,True,240)]
 with tempfile.TemporaryDirectory() as d:
  d=Path(d);probe=d/'Probe.java'
  checks='\n'.join(f'if(Viewport.width({w},{h},{str(wide).lower()})!={expected})throw new AssertionError("case {i}");' for i,(w,h,wide,expected) in enumerate(cases))
  checks+='''
  int[][] surfaces={{1920,1080},{2400,1080},{2520,1080},{1000,500},{3000,500},{640,160}};
  for(int[] size:surfaces){
   int width=Viewport.width(size[0],size[1],true);
   float s=Viewport.scale(size[0],size[1],width,true);
   if(width*s+0.01f<size[0]||160*s+0.01f<size[1])throw new AssertionError("uncovered edge");
   float fitted=Viewport.scale(size[0],size[1],240,false);
   if(240*fitted>size[0]+0.01f||160*fitted>size[1]+0.01f)throw new AssertionError("original cropped");
  }
  if(Viewport.scale(0,0,240,true)!=0)throw new AssertionError("empty surface");
  '''
  probe.write_text('import org.shrek2.research.Viewport; public class Probe {public static void main(String[] args){'+checks+'}}')
  subprocess.run([str(a.jdk/'bin/javac'),'-d',str(d),str(ROOT/'android/app/src/main/java/org/shrek2/research/Viewport.java'),str(probe)],check=True)
  subprocess.run([str(a.jdk/'bin/java'),'-cp',str(d),'Probe'],check=True)
 result={'java_viewport_cases':len(cases),'fill_and_fit_surface_cases':6,'empty_scale_refusals':1,'width_min':240,'width_max':640,'height':160,'mismatches':0,'scope':'Real Java size and uniform scale helper executed with JDK17; layout and WindowInsets require Android device testing.'}
 (ROOT/'docs/android_viewport_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
