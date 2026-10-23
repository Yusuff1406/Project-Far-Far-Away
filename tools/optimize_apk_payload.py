"""Lossless APK payload compression, before alignment and signing."""
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

def compress_music(apk):
    apk=Path(apk);before=apk.stat().st_size;temp=apk.with_suffix('.music.tmp');count=0
    with ZipFile(apk) as source, ZipFile(temp,'w',compresslevel=9) as target:
        for entry in source.infolist():
            data=source.read(entry.filename)
            if entry.filename.startswith('assets/') and entry.filename.endswith('.wav') and not entry.filename.startswith('assets/session/audio/'):
                entry.compress_type=ZIP_DEFLATED;count+=1
            target.writestr(entry,data,compresslevel=9)
    with ZipFile(temp) as check:assert check.testzip() is None
    os.replace(temp,apk)
    return {'music_files_compressed':count,'zip_bytes_before':before,'zip_bytes_after':apk.stat().st_size}
