#!/usr/bin/env python3
"""Runtime world dimensions come from each source scene, rather than scene00 constants."""
import ctypes as C,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));P=C.c_void_p;I=C.c_int32
lib.s2_session_create.argtypes=[C.c_char_p]*4+[C.POINTER(I)];lib.s2_session_create.restype=P;lib.s2_session_destroy.argtypes=[P];lib.s2_session_world_size.argtypes=[P,C.POINTER(I)]
assets=ROOT/'android/app/src/main/assets/session';rows=json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records'];count=0
for row in rows:
 error=I();h=lib.s2_session_create(str(assets/'resources.s2pk').encode(),str(ROOT/f'extracted/scene_{row["scene"]:02d}/scene.s2lv').encode(),str(ROOT/f'collision/scene_{row["scene"]:02d}/scene.s2cl').encode(),str(assets/'sprites').encode(),C.byref(error));assert h,(row['scene'],error.value)
 try:
  size=(I*2)();assert lib.s2_session_world_size(h,size)==0;assert list(size)==[row['width'],row['height']];count+=1
 finally:lib.s2_session_destroy(h)
result=dict(original_scene_dimensions=count,mismatches=0,scope='Resource/session dimension loading only; not gameplay validation of these maps.')
(ROOT/'docs/world_dimensions_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
