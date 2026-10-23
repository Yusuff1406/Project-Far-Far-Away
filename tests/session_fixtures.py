"""Explicit isolation: move the source one-shot intro zone away in old mechanics tests.
Production object bytes are never changed. verify_session_intro covers the real zone.
"""
import atexit,shutil,struct,tempfile
from pathlib import Path
_dirs=[]
def without_intro(raw):
 data=bytearray(raw)
 assert struct.unpack_from('<H',data,16+70*44)[0]==151
 struct.pack_into('<HH',data,18+70*44,3000,0)
 return data
def fixture_scene(path):
 d=tempfile.TemporaryDirectory();_dirs.append(d);target=Path(d.name)/path.name
 target.write_bytes(without_intro(path.read_bytes()))
 meta=path.with_name('objects.json')
 if meta.exists():shutil.copyfile(meta,target.with_name('objects.json'))
 return target
@atexit.register
def cleanup():
 for d in _dirs:d.cleanup()
