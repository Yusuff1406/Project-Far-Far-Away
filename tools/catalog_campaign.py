#!/usr/bin/env python3
"""Recover level-select thumbnails/music linkage via original initializer19648.
This is an offline catalog for subsequent batches, not a claim of playable levels.
"""
import argparse,collections,json,struct,hashlib
from pathlib import Path
from extract import Rom,ROM_BASE,SCENE_TABLE
from extract_session_sfx import GaxOracle
ROOT=Path(__file__).resolve().parents[1]
SUPPORTED={3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 35, 36, 37, 38, 39, 40, 44, 45, 46, 49, 50, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 72, 73, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 147, 148, 149, 150, 151, 152, 68, 74, 144, 146, 153, 154, 155, 156, 157}
IGNORED=set()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);o=GaxOracle(rom.data);o.call(0x08019648);records=[];seen=set();checks=0
 animations={x['address']for x in json.loads((ROOT/'objects/generic_animation_headers.json').read_text())['animations']}
 for slot in range(30):
  ram=0x020033f0+slot*32;row=struct.unpack('<8I',o.u.mem_read(ram,32));delta=row[1]-(ROM_BASE+SCENE_TABLE);assert delta>=0 and delta%32==0;scene=delta//32;assert 0<=scene<30 and scene not in seen;seen.add(scene)
  desc=json.loads((ROOT/f'extracted/scene_{scene:02}/scene.json').read_text());obj=json.loads((ROOT/f'objects/scene_{scene:02}/objects.json').read_text());binary=(ROOT/f'objects/scene_{scene:02}/scene.s2ob').read_bytes();assert binary[:4]==b'S2OB';assert struct.unpack_from('<2I',binary,8)==(len(obj['objects']),scene)
  assert desc['descriptor_offset']==SCENE_TABLE+32*scene and desc['descriptor_words']==list(struct.unpack_from('<8I',rom.data,SCENE_TABLE+32*scene));assert row[2]in animations
  types=collections.Counter(x['type']for x in obj['objects']);secondary=collections.Counter(x['secondary_type_s16']for x in obj['objects']if x['secondary_type_s16']>0)
  unsupported=sorted(set(types)-SUPPORTED-IGNORED);subUnsupported=sorted(set(secondary)-SUPPORTED-IGNORED)
  records.append(dict(original_slot=slot,original_runtime_descriptor=ram,scene=scene,source_scene_descriptor=row[1],level_thumbnail_animation=row[2],thumbnail_order=(row[2]-0x08328440)//24,bonus=bool(row[3]),source_fields_10_14_18=list(row[4:7]),music_song=row[7],width=desc['width_px'],height=desc['height_px'],object_count=len(obj['objects']),primary_types=dict(sorted(types.items())),secondary_types=dict(sorted(secondary.items())),unported_primary_types=unsupported,unported_secondary_types=subUnsupported,ignored_primary_types=sorted(set(types)&IGNORED),playable_in_current_native_session=scene in[0, 1, 2, 13, 17, 25, 14, 9, 11, 8, 4, 10, 23, 21, 29, 24, 3, 19, 22, 28, 12, 5, 20, 15, 16, 26, 7, 6, 18, 27],geometry_assets_extracted=True,objects_assets_extracted=True,collision_assets_extracted=(ROOT/f'collision/scene_{scene:02}/scene.s2cl').is_file(),thumbnail_in_native_package=True))
  checks+=4
 assert seen==set(range(30));records.sort(key=lambda x:x['thumbnail_order']);assert[x['thumbnail_order']for x in records]==list(range(30));checks+=2
 # Original thumbnail sequence gives five chapters of five thumbnails then five bonuses.
 # Keep that grouping explicit without inventing titles or claiming script readiness.
 batches=[dict(thumbnail_range=[i,i+4],scenes=[x['scene']for x in records[i:i+5]],unported_primary_types=sorted(set().union(*(set(x['unported_primary_types'])for x in records[i:i+5]))))for i in range(0,30,5)]
 data=dict(rom_sha256=rom.sha256,original_initializer='0x08019648',catalog_source='30 original runtime records at020033F0, stride32; sorted by original thumbnail animation address',records=records,batches=batches,scope='Stage81: native controllers connect all25 story scenes. Host source/controller and placement-fixture validation; uninterrupted campaign and Android device not certified. All five bonus modes connected; original route/device validation remains separate.')
 (ROOT/'objects/campaign_catalog.json').write_text(json.dumps(data,indent=2)+'\n');report=dict(source_records=30,verified_field_groups=checks,original_thumbnail_order=[x['scene']for x in records],batches=batches,mismatches=0,device_tested=False);(ROOT/'docs/level_batch_readiness.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
