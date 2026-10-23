#!/usr/bin/env python3
"""Recreate local game resources from the user's hash-verified ROM; never fetch a ROM."""
import argparse, concurrent.futures, hashlib, importlib.util, json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA256='2ec32cb8c69ff8bbe01b7039ee001105f92ee686b251d26060f9bdb6751f3b80'

def run(script, *args):
    print('RUN',script,flush=True)
    subprocess.run([sys.executable,str(ROOT/'tools'/script),*map(str,args)],cwd=ROOT,check=True)

def verify_assets():
    expected=json.loads((ROOT/'tools/assets_expected.json').read_text())['files']
    base=ROOT/'android/app/src/main/assets'
    missing=[];different=[]
    for name,entry in expected.items():
        p=base/name
        if not p.is_file():missing.append(name)
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:different.append(name)
    unexpected=sorted(str(p.relative_to(base)) for p in base.rglob('*') if p.is_file() and not any(part.startswith('.') for part in p.relative_to(base).parts) and str(p.relative_to(base)) not in expected)
    if missing or different or unexpected:
        raise RuntimeError('Resource verification failed: '+json.dumps({'missing':missing,'different':different,'unexpected':unexpected}))
    print('PASS: all '+str(len(expected))+' runtime assets match the audited Stage110 snapshot',flush=True)
    return len(expected)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path);ap.add_argument('--jobs',type=int,default=2,choices=range(1,9))
    ap.add_argument('--skip-audio',action='store_true',help='Development only: prepare graphics/data; APK preflight will reject incomplete audio.')
    a=ap.parse_args();rom=a.rom.resolve()
    if not rom.is_file() or hashlib.sha256(rom.read_bytes()).hexdigest()!=SHA256:
        ap.error('A matching original ROM is required (SHA-256 '+SHA256+'). No output has been generated.')
    missing=[m for m in ['PIL','capstone','unicorn','numpy','scipy'] if importlib.util.find_spec(m) is None]
    if missing: ap.error('Missing Python dependencies: '+', '.join(missing)+'. Install: python3 -m pip install -r requirements-audit.txt')
    for folder in ['docs','previews','objects','android/app/src/main/assets','android/app/src/main/assets/frontend','android/app/src/main/assets/session','android/app/src/main/assets/campaign/music']:
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    run('extract.py',rom,'--out',ROOT/'extracted')
    run('extract_sprites.py',rom)
    run('extract_collision.py',rom)
    run('extract_scene_objects.py',rom)
    run('extract_generic_runtime.py',rom)
    run('extract_generic_scripts.py',rom)
    run('extract_sprite_contacts.py',rom)
    run('extract_dialogue_resources.py',rom)
    data=rom.read_bytes();address=0x08024cdc
    # Pickup-manager message parameters, previously a manually retained JSON file.
    (ROOT/'objects/coin_pickup_resources.json').write_text(json.dumps({'rom_sha256':SHA256,'blocks':{str(address):data[address-0x08000000:address-0x08000000+16].hex()}},indent=2)+'\n')
    run('package_native_session.py')
    run('catalog_campaign.py',rom)
    assets=ROOT/'android/app/src/main/assets'
    for n in range(30):
        for source,dest in [(ROOT/f'extracted/scene_{n:02}/scene.s2lv',assets/f'scenes/scene_{n:02}.s2lv'),(ROOT/f'collision/scene_{n:02}/scene.s2cl',assets/f'collision/scene_{n:02}.s2cl'),(ROOT/f'objects/scene_{n:02}/scene.s2ob',assets/f'objects/scene_{n:02}.s2ob')]:
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    for name in ['generic_animation_headers.json','sprite_contact_resources.json','generic_script_resources.s2rs']:
        shutil.copyfile(ROOT/'objects'/name,assets/'objects'/name)
    (assets/'sprites').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'sprites/shrek_ogre/bank.s2sp',assets/'sprites/shrek_ogre.s2sp')
    run('package_campaign.py',rom)
    run('package_campaign_player.py',rom)
    run('extract_frontend.py',rom)
    if a.skip_audio:
        print('Graphics/data prepared; audio intentionally incomplete.',flush=True);return
    commands=[('extract_menu_sfx.py',),('extract_complete_sfx.py',),('extract_scene_music.py',),('extract_bonus_music.py',),('extract_campaign_music.py',),('extract_boot_music.py',),('extract_menu_music.py',),('extract_credits_music.py',),('extract_epilogue_music.py',),('extract_unused_music.py','0x0820b76c'),('extract_unused_music.py','0x0820cf24')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        futures=[pool.submit(run,cmd[0],rom,*cmd[1:]) for cmd in commands]
        for f in futures:f.result()
    count=verify_assets()
    (assets/'.prepared.json').write_text(json.dumps({'rom_sha256':SHA256,'assets_verified':count})+'\n')

if __name__=='__main__':main()
