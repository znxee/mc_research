"""MC3 Remix Xbox bootstrap + runtime INI/external i386 XMOD loader.

Strict known-build XBE patcher: an added preload section, startup shim and
ABI-preserving BeginFrame shims. Never edits the source XBE or source XISO.
Only bootstrap diagnostics are baked; gameplay INI/modules are read from DVD.
"""
import os
import argparse,configparser,hashlib,json,pathlib,shlex,shutil,struct,subprocess

HERE=pathlib.Path(__file__).resolve().parent
SOURCE=HERE/'modloader/xbox'
ORIGINAL_SHA256='0b3d81a02834e57864a601d473d5296cc0a2463e4b837373d91030f751fa51a3'
BASE=0x10000;PAYLOAD=0x58B000;CFG=0x58D000;STATS=0x58C000
ENTRY_KEY=0xA8FC57AB
PAYLOAD_SIZE=0x1D000
HOOKS=(0x12316,0x1ACFD,0x1BA24,0x1BA83,0x1FD7A,0x2D5408)
BUILTINS={'frontend_no_timeout':1}
MODULE_MASK_OFFSET=20+64*36
def align(x,n):return (x+n-1)&-n
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(b):return hashlib.sha1(struct.pack('<I',len(b))+b).digest()
def u32(b,o):return struct.unpack_from('<I',b,o)[0]

class Xbe:
    def __init__(self,data):
        self.data=data
        if len(data)<0x184 or data[:4]!=b'XBEH':raise ValueError('Not an XBE')
        self.base=u32(data,0x104);self.headers=u32(data,0x108)
        n=u32(data,0x11c);table=u32(data,0x120)-self.base
        if not 0<n<128 or table<0x184 or table+n*56>self.headers or self.headers>len(data):
            raise ValueError('Invalid section/header bounds')
        self.sections=[]
        for i in range(n):
            at=table+i*56;vals=struct.unpack_from('<9I',data,at)
            flags,va,vs,raw,rs,name,ref,head,tail=vals
            if raw+rs>len(data) or not 0<=name-self.base<self.headers:raise ValueError('Section out of file/header')
            end=data.find(b'\0',name-self.base,self.headers)
            if end<0:raise ValueError('Unterminated section name')
            s=dict(flags=flags,va=va,size=vs,raw=raw,raw_size=rs,
                   name=data[name-self.base:end].decode('ascii'),header=at)
            if digest(data[raw:raw+rs])!=data[at+36:at+56]:raise ValueError('Section digest mismatch: '+s['name'])
            self.sections.append(s)
    def offset(self,va,size=1):
        if self.base<=va and va+size<=self.base+self.headers:return va-self.base
        for s in self.sections:
            if s['va']<=va and va+size<=s['va']+s['raw_size']:return s['raw']+va-s['va']
        raise ValueError('VA not file-backed: '+hex(va))
    def summary(self):
        return dict(sha256=sha(self.data),bytes=len(self.data),base=hex(self.base),
                    entry=hex(u32(self.data,0x128)^ENTRY_KEY),sections=len(self.sections),
                    all_digests_valid=True,init_flags=hex(u32(self.data,0x124)),
                    stats_va=hex(STATS) if any(s['name']=='.mc3boot' for s in self.sections) else None)

def configuration(path,runtime=False):
    if runtime:
        return 1,struct.pack('<5I',0x4358334D,3,1,300,0).ljust(4096,b'\0')
    c=configparser.ConfigParser(interpolation=None,inline_comment_prefixes=(';','#'))
    c.optionxform=str
    with pathlib.Path(path).open(encoding='utf-8-sig') as f:c.read_file(f)
    if set(c.sections())-{'loader','mods','patches','boot'}:raise ValueError('Unsupported INI section')
    if c.defaults():raise ValueError('DEFAULT section is not supported')
    mask=0
    for section in ('mods','patches'):
        for k,v in c.items(section) if c.has_section(section) else []:
            if v.strip() in ('0','off','false','disabled'):continue
            if section!='mods' or k not in BUILTINS or v.strip()!='1':
                raise ValueError('Unsupported Xbox built-in/mode: '+section+': '+k+'='+v)
            mask|=BUILTINS[k]
    opts=dict(c.items('loader')) if c.has_section('loader') else {}
    if set(opts)-{'enabled','serial','heartbeat'}:raise ValueError('Unsupported loader option')
    enabled=int(opts.get('enabled','1'));serial=int(opts.get('serial','1'));beat=int(opts.get('heartbeat','300'))
    if enabled not in (0,1) or serial not in (0,1) or not 0<=beat<=1000000:raise ValueError('Invalid loader settings')
    args=[];ids=set()
    for k,v in c.items('boot') if c.has_section('boot') else []:
        key=k.encode('ascii');value=v.encode('ascii')
        if not key or len(value)>31 or any(x<32 or x>126 for x in key+value):
            raise ValueError('Boot keys/values must be printable ASCII; values <=31 bytes')
        ident=int.from_bytes(key[:4].ljust(4,b'\0'),'little')
        if ident in ids:raise ValueError('Boot key first-four-character collision: '+k)
        ids.add(ident);args.append(struct.pack('<I32s',ident,value))
    if len(args)>64:raise ValueError('Too many boot arguments')
    blob=struct.pack('<5I',0x4358334D,2,serial,beat,len(args))+b''.join(args)
    blob=blob.ljust(MODULE_MASK_OFFSET,b'\0')+struct.pack('<I',mask)
    return enabled,blob.ljust(4096,b'\0')

def msys_path(p):
    p=pathlib.Path(p).resolve().as_posix()
    if len(p)<3 or p[1:3]!=':/':raise ValueError('Expected local drive path')
    return '/'+p[0].lower()+p[2:]

def compile_payload(directory,bash=pathlib.Path(os.path.join(os.environ.get('MSYS_DIR', ''), 'usr/bin/bash.exe'))):
    directory.mkdir(parents=True,exist_ok=True)
    q=lambda p:shlex.quote(msys_path(p))
    cpp=directory/'mc3boot_xbox.o';runtime=directory/'runtime.o';mod=directory/'module_loader.o';asm=directory/'entry.o';pe=directory/'payload.exe';binary=directory/'payload.bin'
    flags='-std=gnu++11 -m32 -Os -ffreestanding -fno-stack-protector -fno-pic -fno-pie -fno-exceptions -fno-rtti -fno-ident -fno-asynchronous-unwind-tables -fno-unwind-tables -mno-sse -mno-mmx -msoft-float -mpreferred-stack-boundary=2 -mincoming-stack-boundary=2'
    commands=[f'/mingw64/bin/g++ {flags} -Wall -Wextra -c {q(SOURCE/"mc3boot_xbox.cpp")} -o {q(cpp)}',
              f'/mingw64/bin/g++ {flags} -Wall -Wextra -c {q(SOURCE/"module_loader.cpp")} -o {q(mod)}',
              f'/mingw64/bin/g++ {flags} -Wall -Wextra -c {q(SOURCE/"runtime.cpp")} -o {q(runtime)}',
              f'/mingw64/bin/gcc -m32 -c {q(SOURCE/"entry.S")} -o {q(asm)}',
              f'/mingw64/bin/ld -m i386pe --image-base 0 --disable-reloc-section --entry _mc3x_entry -T {q(SOURCE/"payload.ld")} -o {q(pe)} {q(asm)} {q(cpp)} {q(mod)} {q(runtime)}',
              f'/mingw64/bin/objcopy -O binary -j .text -j .data -j .mc3cfg -j .runtime -j .work {q(pe)} {q(binary)}']
    for command in commands:subprocess.run([str(bash),'-lc','export PATH=/mingw64/bin:$PATH; '+command],check=True)
    nm=subprocess.check_output([str(bash),'-lc',f'export PATH=/mingw64/bin:$PATH; /mingw64/bin/nm -n {q(pe)}'],text=True)
    symbols={}
    for line in nm.splitlines():
        v=line.split()
        if len(v)==3:
            try:symbols[v[2]]=int(v[0],16)
            except ValueError:pass
    if symbols.get('_mc3x_entry')!=PAYLOAD or symbols.get('_mc3x_stats')!=STATS or symbols.get('_mc3x_config')!=CFG:
        raise ValueError('Unexpected payload section addresses')
    if symbols.get('__CTOR_LIST__'):raise ValueError('Unexpected C++ constructor dependency')
    data=binary.read_bytes()
    if not 0x2000<len(data)<=PAYLOAD_SIZE:raise ValueError('Payload outside reserved region')
    manifest=dict(base=PAYLOAD,entry=symbols['_mc3x_entry'],frame_hook=symbols['_mc3x_frame_hook'],stats=STATS,config=CFG)
    manifest['exports']={k:v for k,v in symbols.items() if k.startswith('_mc3x_')}
    return data.ljust(PAYLOAD_SIZE,b'\0'),manifest

def patch_xbe(original,payload,symbols,config,runtime=True):
    image=Xbe(original)
    if sha(original)!=ORIGINAL_SHA256:raise ValueError('Unsupported/modified XBE; original Remix USA build required')
    enabled,cfg=configuration(config,runtime)
    if not enabled:return original,dict(enabled=False,original_sha256=sha(original))
    if image.base!=BASE or u32(original,0x128)^ENTRY_KEY!=0x1299F:raise ValueError('Unexpected retail entry/key')
    if align(max(s['va']+s['size'] for s in image.sections),4096)!=PAYLOAD:raise ValueError('Payload VA overlaps image')
    new=bytearray(original);payload=bytearray(payload);payload[CFG-PAYLOAD:CFG-PAYLOAD+4096]=cfg
    imports=[]
    if runtime or u32(cfg,MODULE_MASK_OFFSET)&1:
        # Existing 154-entry kernel IAT ends at 0x447948, followed by zero
        # alignment padding. Extend in place: original import slots stay put.
        if u32(original,0x158)^0x5B6D40B6!=0x4476E0:raise ValueError('Unexpected kernel IAT')
        at=image.offset(0x447948,24)
        if any(original[at:at+24]):raise ValueError('Kernel IAT padding is not empty')
        struct.pack_into('<I',new,at,0x800000CC) # NtProtectVirtualMemory, ordinal 204.
        imports=['NtProtectVirtualMemory@16 (204)']
    for site in HOOKS:
        off=image.offset(site,5);old=original[off:off+5]
        if old[0]!=0xE8 or site+5+struct.unpack_from('<i',old,1)[0]!=0x2D1830:raise ValueError('Unexpected BeginFrame call: '+hex(site))
        new[off:off+5]=b'\xe8'+struct.pack('<i',symbols['frame_hook']-site-5)
    # Move the complete section table into verified unused header padding.
    table=align(image.headers,16);count=len(image.sections)+1;name_at=table+count*56
    refs_at=align(name_at+len(b'.mc3boot\0'),2);header_end=align(refs_at+4,4)
    first_raw=min(s['raw'] for s in image.sections if s['raw_size'])
    if header_end>first_raw or any(original[image.headers:first_raw]):raise ValueError('No clean header space')
    oldtable=u32(original,0x120)-BASE
    new[table:table+(count-1)*56]=original[oldtable:oldtable+(count-1)*56]
    new[name_at:name_at+9]=b'.mc3boot\0';new[refs_at:refs_at+4]=b'\0'*4
    raw=align(len(new),4096);new.extend(b'\0'*(raw-len(new)));new.extend(payload)
    added=struct.pack('<9I',7,PAYLOAD,len(payload),raw,len(payload),BASE+name_at,0,BASE+refs_at,BASE+refs_at+2)+digest(payload)
    new[table+(count-1)*56:table+count*56]=added
    for off,value in ((0x108,first_raw),(0x10c,align(PAYLOAD+len(payload)-BASE,4096)),
                      (0x11c,count),(0x120,BASE+table),(0x128,symbols['entry']^ENTRY_KEY)):
        struct.pack_into('<I',new,off,value)
    for i,s in enumerate(image.sections):new[table+i*56+36:table+i*56+56]=digest(new[s['raw']:s['raw']+s['raw_size']])
    checked=Xbe(new)
    report=dict(enabled=True,original_sha256=sha(original),output=checked.summary(),symbols=symbols,
                hook_sites=[hex(x) for x in HOOKS],config_sha256=sha(cfg),
                signature='RSA not regenerated; modified/debug BIOS required',runtime_modules_supported=runtime,
                builtin_modules=[k for k,bit in BUILTINS.items() if u32(cfg,MODULE_MASK_OFFSET)&bit],
                added_kernel_imports=imports,runtime_ini=runtime)
    return bytes(new),report

def xiso_entry(stream,name):
    stream.seek(0x10000);header=stream.read(2048)
    if header[:20]!=b'MICROSOFT*XBOX*MEDIA':raise ValueError('Only partition-offset-zero XISO is supported')
    sector,size=struct.unpack_from('<II',header,20);start=sector*2048
    stream.seek(start);root=stream.read(size);visited=set();todo=[0]
    while todo:
        off=todo.pop()
        if off in visited or off+14>len(root):raise ValueError('Bad XISO root tree')
        visited.add(off);left,right,sec,length,attrs,n=struct.unpack_from('<HHIIBB',root,off)
        if off+14+n>len(root):raise ValueError('Bad XISO directory name')
        found=root[off+14:off+14+n].decode('ascii')
        if found.lower()==name.lower() and not attrs&16:return start+off,sec,length
        todo.extend(v*4 for v in (left,right) if v)
    raise ValueError('XISO root file not found: '+name)

def patch_iso(source,destination,xbe):
    source=pathlib.Path(source);destination=pathlib.Path(destination)
    if source.resolve()==destination.resolve() or destination.exists():raise ValueError('ISO destination must be a new, separate file')
    with source.open('rb') as f:
        entry,sector,size=xiso_entry(f,'default.xbe');f.seek(sector*2048);original=f.read(size)
        if sha(original)!=ORIGINAL_SHA256:raise ValueError('ISO contains unsupported/modified default.xbe')
    destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
    with destination.open('r+b') as f:
        f.seek(0,2);new_sector=align(f.tell(),2048)//2048;f.write(b'\0'*(new_sector*2048-f.tell()))
        f.write(xbe);f.write(b'\0'*(align(len(xbe),2048)-len(xbe)))
        f.seek(entry+4);f.write(struct.pack('<II',new_sector,len(xbe)))
        _,actual_sector,actual_size=xiso_entry(f,'default.xbe');f.seek(actual_sector*2048)
        if actual_size!=len(xbe) or f.read(actual_size)!=xbe:raise ValueError('XISO verification failed')
    return dict(output=str(destination),old_sector=sector,new_sector=new_sector,dirent=hex(entry),xbe_sha256=sha(xbe))

def root_entries(stream):
    stream.seek(0x10000);header=stream.read(2048)
    if header[:20]!=b'MICROSOFT*XBOX*MEDIA':raise ValueError('Only offset-zero XISO')
    sector,size=struct.unpack_from('<II',header,20)
    if size>262144:raise ValueError('Root directory too large')
    stream.seek(sector*2048);data=stream.read(size);todo=[0];seen=set();entries=[]
    while todo:
        at=todo.pop()
        if at in seen or at+14>len(data):raise ValueError('Bad root tree')
        seen.add(at);left,right,sec,n,attrs,length=struct.unpack_from('<HHIIBB',data,at)
        if at+14+length>len(data):raise ValueError('Bad root name')
        name=data[at+14:at+14+length].decode('ascii')
        entries.append(dict(name=name,sector=sec,size=n,attrs=attrs))
        todo.extend(v*4 for v in (left,right) if v)
    return entries

def directory_tree(entries):
    ordered=sorted(entries,key=lambda e:e['name'].upper());data=bytearray();names=set()
    def node(items):
        if not items:return 0
        mid=len(items)//2;e=items[mid];name=e['name'].encode('ascii')
        if not name or len(name)>42 or e['name'].upper() in names:raise ValueError('Bad/duplicate XISO name')
        names.add(e['name'].upper());size=align(14+len(name),4)
        if len(data)%2048+size>2048:data.extend(b'\0'*(2048-len(data)%2048))
        at=len(data)
        if at//4>65535:raise ValueError('XISO directory offset overflow')
        data.extend(struct.pack('<HHIIBB',0,0,e['sector'],e['size'],e['attrs'],len(name))+name)
        data.extend(b'\0'*(align(len(data),4)-len(data)))
        left=node(items[:mid]);right=node(items[mid+1:])
        struct.pack_into('<HH',data,at,left//4,right//4)
        return at
    if not ordered:raise ValueError('Empty directory')
    node(ordered)
    return bytes(data).ljust(align(len(data),2048),b'\0')

def runtime_iso(source,destination,xbe,files):
    source=pathlib.Path(source);destination=pathlib.Path(destination)
    if source.resolve()==destination.resolve() or destination.exists():raise ValueError('New separate XISO required')
    with source.open('rb') as f:
        entries=root_entries(f);_,sector,n=xiso_entry(f,'default.xbe');f.seek(sector*2048)
        if sha(f.read(n))!=ORIGINAL_SHA256:raise ValueError('Original Remix USA XISO required')
    contents={'default.xbe':xbe}
    for name,blob in files.items():
        if name.lower()=='default.xbe' or '/' in name or '\\' in name:raise ValueError('Root files only')
        contents[name]=bytes(blob)
    if len({n.upper() for n in contents})!=len(contents):raise ValueError('Duplicate root replacement')
    for name in contents:
        if not name or len(name.encode('ascii'))>42:raise ValueError('XISO root filename limit')
    destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
    with destination.open('r+b') as f:
        f.seek(0,2)
        for name,blob in contents.items():
            sector=align(f.tell(),2048)//2048;f.write(b'\0'*(sector*2048-f.tell()));f.write(blob)
            f.write(b'\0'*(align(len(blob),2048)-len(blob)))
            existing=next((e for e in entries if e['name'].upper()==name.upper()),None)
            if existing:
                if existing['attrs']&16:raise ValueError('Refuse replacing a directory')
                existing.update(sector=sector,size=len(blob))
            else:entries.append(dict(name=name,sector=sector,size=len(blob),attrs=32))
        root_sector=f.tell()//2048;directory=directory_tree(entries);f.write(directory)
        f.seek(0x10000+20);f.write(struct.pack('<II',root_sector,len(directory)))
        for name,blob in contents.items():
            _,sector,n=xiso_entry(f,name);f.seek(sector*2048)
            if n!=len(blob) or f.read(n)!=blob:raise ValueError('XISO read-back mismatch: '+name)
        actual=root_entries(f)
        if sorted(e['name'].upper() for e in actual)!=sorted(e['name'].upper() for e in entries):raise ValueError('Root mismatch')
    return dict(output=str(destination),root_sector=root_sector,files={k:sha(v) for k,v in contents.items()})

def disc_files(ini,mods):
    files={'mc3boot.ini':pathlib.Path(ini).read_bytes()}
    import mc3_xbox_mod
    for p in mods:
        data=p.read_bytes();mc3_xbox_mod.parse(data)
        if p.suffix!='.xmod' or any(p.name.upper()==k.upper() for k in files):raise ValueError('Unique .xmod root filenames required')
        files[p.name]=data
    return files

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    i=sub.add_parser('inspect');i.add_argument('xbe',type=pathlib.Path)
    b=sub.add_parser('build');b.add_argument('--xbe',required=True,type=pathlib.Path);b.add_argument('--ini',type=pathlib.Path,default=SOURCE/'mc3boot.ini')
    b.add_argument('--out',required=True,type=pathlib.Path);b.add_argument('--build-dir',required=True,type=pathlib.Path)
    b.add_argument('--iso',type=pathlib.Path);b.add_argument('--out-iso',type=pathlib.Path)
    b.add_argument('--runtime',action='store_true',default=True,help='Runtime INI is now the default (flag retained for compatibility)')
    b.add_argument('--mod',action='append',default=[],type=pathlib.Path,help='External .xmod file to add at XISO root')
    p=sub.add_parser('pack',help='Repack original XISO with an existing loader XBE and new runtime INI/modules; no compilation')
    p.add_argument('--xbe',required=True,type=pathlib.Path);p.add_argument('--ini',required=True,type=pathlib.Path)
    p.add_argument('--iso',required=True,type=pathlib.Path);p.add_argument('--out-iso',required=True,type=pathlib.Path)
    p.add_argument('--mod',action='append',default=[],type=pathlib.Path)
    a=ap.parse_args()
    if a.action=='inspect':print(json.dumps(Xbe(a.xbe.read_bytes()).summary(),indent=2));return
    if a.action=='pack':
        xbe=a.xbe.read_bytes();image=Xbe(xbe)
        if image.base!=BASE or u32(xbe,0x128)^ENTRY_KEY!=PAYLOAD or not any(s['name']=='.mc3boot' for s in image.sections):
            raise ValueError('Expected an existing mc3boot Xbox XBE')
        cfg=image.offset(CFG,8)
        if struct.unpack_from('<2I',xbe,cfg)!=(0x4358334D,3):raise ValueError('Runtime-config v3 loader required')
        report=runtime_iso(a.iso,a.out_iso,xbe,disc_files(a.ini,a.mod))
        a.out_iso.with_suffix('.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return
    if a.out.exists() or a.out.resolve()==a.xbe.resolve():raise ValueError('XBE destination must be a new, separate file')
    if bool(a.iso)!=bool(a.out_iso):raise ValueError('--iso and --out-iso must be used together')
    if a.out_iso and (a.out_iso.exists() or a.out_iso.resolve()==a.iso.resolve()):
        raise ValueError('ISO destination must be a new, separate file')
    payload,symbols=compile_payload(a.build_dir)
    result,report=patch_xbe(a.xbe.read_bytes(),payload,symbols,a.ini,a.runtime)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(result)
    if a.iso:
        report['iso']=runtime_iso(a.iso,a.out_iso,result,disc_files(a.ini,a.mod))
    a.out.with_suffix('.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
