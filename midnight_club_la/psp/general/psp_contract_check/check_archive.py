import os
from pathlib import Path
import json,subprocess,hashlib,zlib,struct
H=Path('research/psp_contract');exe=Path('build/win32/Release/content_test.exe').resolve();archive=Path(os.path.join(os.environ.get('MC3_ALPHA_HOSTFS', ''), 'MCLA.DAT'))
listing=subprocess.run([str(exe),'archive',str(archive)],capture_output=True,check=True).stdout
(H/'native_archive.tsv').write_bytes(listing)
index=json.loads(Path(os.path.join(os.environ.get('MC_WORK_DIR', ''), 'psp_static_2026-09-29/mcla/archives.json')).read_text())[0]['entries']
results=[]
for name in ['resources/city/la_dawn_clear.psppck','resources/city/tokyo_dawn_clear.psppck','resources/prop/la_dawn_clear_props.psppck']:
 b=subprocess.run([str(exe),'archive',str(archive),name],capture_output=True,check=True).stdout
 e=next(x for x in index if x['name']==name)
 with Path(os.path.join(os.environ.get('MC_RESEARCH_ASSETS', ''), 'mcla psp/PSP_GAME/USRDIR/PSPASSET.DAT')).open('rb') as src:
  src.seek(e['offset']);raw=src.read(e['stored'])
 expected=zlib.decompress(raw,-15) if e['stored']!=e['size'] else raw
 assert b==expected
 (H/Path(name).name).write_bytes(b)
 base,kind,version,size=struct.unpack_from('<4I',b);assert size+128==len(b)
 row={'name':name,'bytes':len(b),'native_equal_original':True,'sha256':hashlib.sha256(b).hexdigest(),'type':kind}
 if kind==67:
  ptr=lambda p:struct.unpack_from('<I',b,p)[0]-base+128
  pool=ptr(128+780);logical=struct.unpack_from('<I',b,128+788)[0]
  dz=zlib.decompressobj();out=dz.decompress(b[pool:]);assert dz.eof and len(out)==logical
  consumed=len(b)-pool-len(dz.unused_data)
  row.update(pool_offset=pool,expanded_pool_bytes=logical,zlib_consumed=consumed,compacted_gap=consumed&~15,pool_sha256=hashlib.sha256(out).hexdigest())
 results.append(row)
report={'archive_bytes':archive.stat().st_size,'native_unique_entry_names':len(listing.splitlines()),'original_index_entries':len(index),'native_original_entries':results}
(H/'native_archive_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
