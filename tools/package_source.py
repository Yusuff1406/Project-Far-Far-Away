#!/usr/bin/env python3
"""Make a code-only archive, even after local ROM extraction and compilation."""
import argparse,zipfile
from pathlib import Path
from source_inventory import ROOT,source_files

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--output",type=Path,default=ROOT/"dist/Project_Far_Far_Away_clean_source.zip");a=ap.parse_args()
    output=a.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in source_files():z.write(p,Path("project-far-far-away")/p.relative_to(ROOT))
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:raise RuntimeError("Invalid archive")
        print(str(output)+": "+str(len(z.namelist()))+" source files")
if __name__=="__main__":main()
