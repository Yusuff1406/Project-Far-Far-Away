#!/usr/bin/env python3
"""Keep original dialogue font bytes; scripts/English text already inS2RS slice."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 r=Path(sys.argv[1]).read_bytes();blocks={}
 for start,size in [(0x30f9ac,32),(0x30fbac,520+217*128)]:blocks[str(0x8000000+start)]=r[start:start+size].hex()
 report={'blocks':blocks,'font_address':'0x0830FBAC','palette_address':'0x0830F9AC','glyphs':217,'glyph_size':[16,16],'bpp':4,'line_height':12,'text_area':[65,18,142,43],'text_language':'English','rom_sha256':hashlib.sha256(r).hexdigest()}
 (ROOT/'objects/dialogue_font_resources.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k!='blocks'})
if __name__=='__main__':main()
