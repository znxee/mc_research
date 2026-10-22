"""Build/inspect native relocatable i386 .xmod containers. Never accepts PS2 .mod."""
import os
import argparse,json,pathlib,re,shlex,struct,subprocess
import mc3_xbox_boot as boot
MAGIC=0x4D58334D;TARGET=0x58433301;MAX_IMAGE=65536;MAX_RELOCS=1024
def fnv(data,seed=2166136261):
    for b in data:seed=((seed^b)*16777619)&0xffffffff
    return seed
def parse(data):
    if len(data)<64:raise ValueError('Truncated XMOD header')
    h=struct.unpack_from('<16I',data)
    magic,version,machine,abi,target,header,n,entry,count,checksum,flags,*reserved=h
    if (magic,version,machine,abi,target,header)!=(MAGIC,1,0x14c,1,TARGET,64):raise ValueError('Wrong XMOD magic/version/architecture/ABI/target')
    if flags or any(reserved) or not 0<n<=MAX_IMAGE or entry>=n or count>MAX_RELOCS:raise ValueError('Invalid XMOD limits/flags')
    if len(data)!=64+n+count*4:raise ValueError('Truncated/extra XMOD bytes')
    if fnv(data[64:])!=checksum:raise ValueError('XMOD checksum mismatch')
    image=data[64:64+n];relocs=struct.unpack_from('<'+'I'*count,data,64+n) if count else ()
    occupied=set()
    for off in relocs:
        if n<4 or off>n-4 or any(p in occupied for p in range(off,off+4)):raise ValueError('Invalid/overlapping relocation')
        if struct.unpack_from('<I',image,off)[0]>=n:raise ValueError('Relocation points outside image')
        occupied.update(range(off,off+4))
    return dict(image=image,entry=entry,relocs=relocs,checksum=checksum)
def pack(image,entry,relocs):
    body=bytes(image)+b''.join(struct.pack('<I',v) for v in relocs)
    result=struct.pack('<16I',MAGIC,1,0x14c,1,TARGET,64,len(image),entry,len(relocs),fnv(body),0,0,0,0,0,0)+body
    parse(result);return result
def from_pe(data):
    if data[:2]!=b'MZ':raise ValueError('Not PE')
    pe=boot.u32(data,0x3c)
    if data[pe:pe+4]!=b'PE\0\0':raise ValueError('Bad PE signature')
    machine,sections=struct.unpack_from('<HH',data,pe+4);opt_size=struct.unpack_from('<H',data,pe+20)[0];opt=pe+24
    if machine!=0x14c or struct.unpack_from('<H',data,opt)[0]!=0x10b or boot.u32(data,opt+28)!=0:raise ValueError('Expected i386 PE32 at base zero')
    table=opt+opt_size;sects=[]
    for i in range(sections):
        at=table+i*40;name=data[at:at+8].split(b'\0')[0].decode('ascii');vs,va,rs,raw=struct.unpack_from('<4I',data,at+8)
        if raw+rs>len(data):raise ValueError('PE section bounds')
        if name.startswith(('.CRT','.ctors','.dtors','.tls')) and (vs or rs):raise ValueError('Constructors/TLS unsupported')
        sects.append(dict(name=name,va=va,vs=vs,rs=rs,raw=raw,flags=boot.u32(data,at+36)))
    kept=[s for s in sects if s['name'] not in ('.reloc',) and not s['name'].startswith(('.debug','/'))]
    n=max(s['va']+max(s['vs'],s['rs']) for s in kept)
    if not 0<n<=MAX_IMAGE:raise ValueError('PE image too large')
    image=bytearray(n)
    for s in kept:image[s['va']:s['va']+s['rs']]=data[s['raw']:s['raw']+s['rs']]
    # All-zero import terminator emitted by GNU ld is harmless; imports are not.
    imp,size=struct.unpack_from('<2I',data,opt+104)
    if size and (imp+size>n or any(image[imp:imp+size])):raise ValueError('PE imports unsupported; use Mc3xApi')
    tls,size=struct.unpack_from('<2I',data,opt+96+9*8)
    if tls or size:raise ValueError('TLS unsupported')
    rva,size=struct.unpack_from('<2I',data,opt+96+5*8);relocs=[]
    if size:
        sec=next((s for s in sects if s['va']<=rva and rva+size<=s['va']+s['rs']),None)
        if not sec:raise ValueError('Bad PE relocation directory')
        raw=sec['raw']+rva-sec['va'];end=raw+size
        while raw<end:
            page,count=struct.unpack_from('<2I',data,raw)
            if count<8 or count%2 or raw+count>end:raise ValueError('Bad PE relocation block')
            for at in range(raw+8,raw+count,2):
                value=struct.unpack_from('<H',data,at)[0];kind=value>>12
                if kind==3:relocs.append(page+(value&4095))
                elif kind:raise ValueError('Only i386 HIGHLOW relocations supported')
            raw+=count
    entry=boot.u32(data,opt+16)
    if not any(s['va']<=entry<s['va']+s['vs'] and s['flags']&0x20000000 for s in kept):raise ValueError('Entry outside executable section')
    return pack(image,entry,relocs)
def build(source,out,directory):
    if out.exists():raise ValueError('Choose a new module output')
    directory.mkdir(parents=True,exist_ok=True);obj=directory/'module.o';pe=directory/'module.exe'
    q=lambda p:shlex.quote(boot.msys_path(p))
    flags='-std=gnu++11 -m32 -Os -ffreestanding -fno-stack-protector -fno-pic -fno-pie -fno-exceptions -fno-rtti -fno-ident -fno-asynchronous-unwind-tables -fno-unwind-tables -mno-sse -mno-mmx -msoft-float -mpreferred-stack-boundary=2 -mincoming-stack-boundary=2'
    bash=os.path.join(os.environ.get('MSYS_DIR', ''), 'usr/bin/bash.exe')
    run=lambda command:subprocess.run([bash,'-lc','export PATH=/mingw64/bin:$PATH; '+command],check=True)
    run(f'/mingw64/bin/g++ {flags} -Wall -Wextra -c {q(source)} -o {q(obj)}')
    sections=subprocess.check_output([bash,'-lc',f'export PATH=/mingw64/bin:$PATH; /mingw64/bin/objdump -h {q(obj)}'],text=True)
    # GNU ld may merge .ctors into .text: reject them before that information
    # disappears, rather than silently skipping native static initialization.
    for name,size in re.findall(r'^\s*\d+\s+(\S+)\s+([0-9a-fA-F]+)\s+',sections,re.M):
        if int(size,16) and name.startswith(('.ctors','.dtors','.CRT','.tls')):
            raise ValueError('Constructors/TLS unsupported: '+name)
    run(f'/mingw64/bin/ld -m i386pe --image-base 0 --enable-reloc-section --entry _mc3x_mod_main -o {q(pe)} {q(obj)}')
    data=from_pe(pe.read_bytes());out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    result=summary(data);out.with_suffix('.json').write_text(json.dumps(result,indent=2));return result
def summary(data):
    m=parse(data);return dict(format='M3XM v1',machine='i386',abi=1,target=hex(TARGET),bytes=len(data),
        image_size=len(m['image']),entry_offset=hex(m['entry']),relocations=len(m['relocs']),checksum=hex(m['checksum']),sha256=boot.sha(data))
def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
    i=sub.add_parser('inspect');i.add_argument('file',type=pathlib.Path)
    b=sub.add_parser('build');b.add_argument('--source',required=True,type=pathlib.Path);b.add_argument('--out',required=True,type=pathlib.Path);b.add_argument('--build-dir',required=True,type=pathlib.Path)
    a=ap.parse_args();r=summary(a.file.read_bytes()) if a.action=='inspect' else build(a.source,a.out,a.build_dir)
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
