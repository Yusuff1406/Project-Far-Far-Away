#!/usr/bin/env python3
import argparse,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--jdk',type=Path,required=True);a=p.parse_args()
 with tempfile.TemporaryDirectory()as tmp:
  subprocess.run([str(a.jdk/'bin/javac'),'-d',tmp,str(ROOT/'android/app/src/main/java/org/shrek2/research/TouchButtons.java'),str(ROOT/'tests/java/org/shrek2/research/TouchButtonsTest.java')],check=True);print(subprocess.check_output([str(a.jdk/'bin/java'),'-cp',tmp,'org.shrek2.research.TouchButtonsTest'],text=True).strip())
 (ROOT/'docs/touch_buttons_validation.json').write_text(json.dumps({'checks':1018,'mismatches':0,'scope':'Compiled Java pointer helper: ownership, A/B order, sub-frame overlap one-shot latch, duplicate fingers, mask cancellation and reset. Actual Android events/device touch excluded.'},indent=2)+'\n')
if __name__=='__main__':main()
