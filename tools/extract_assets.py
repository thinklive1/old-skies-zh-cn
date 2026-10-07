"""Extract only translation-bearing assets from AGS CLIB v30, read-only.

Format reference: AGS Common/data/multifilelib.cpp (Artistic License 2.0).
This independent parser never rewrites the installed game.
"""
from pathlib import Path
import argparse, hashlib, json, struct

def extract(exe, target):
    exe, target = Path(exe), Path(target)
    data = exe.read_bytes()
    if not data.endswith(b'CLIB\x01\x02\x03\x04SIGE'):
        raise ValueError('Missing AGS archive footer')
    base = struct.unpack_from('<q', data, len(data)-20)[0]
    if data[base:base+7] != b'CLIB\x1a\x1e\x00':
        raise ValueError('Only the verified single-library CLIB v30 is supported')
    pos = base+7
    def read(fmt):
        nonlocal pos
        value = struct.unpack_from(fmt, data, pos); pos += struct.calcsize(fmt)
        return value
    def cstr():
        nonlocal pos
        end = data.index(0, pos); value = data[pos:end].decode('cp1252'); pos = end+1
        return value
    flags, n = read('<ii')
    libraries = [cstr() for _ in range(n)]
    if n != 1 or flags != 0:
        raise ValueError('Unexpected archive layout')
    count, = read('<i')
    assets = []
    target.mkdir(parents=True, exist_ok=True)
    for _ in range(count):
        name = cstr(); uid, offset, size = read('<Bqq')
        if uid != 0 or offset < 0 or size < 0 or base+offset+size > len(data):
            raise ValueError('Invalid asset range')
        if Path(name).name != name or '\\' in name or '/' in name:
            raise ValueError('Unsafe archive name')
        blob = data[base+offset:base+offset+size]
        selected = name.lower().endswith(('.dta','.crm','.ttf','.wfn'))
        assets.append(dict(name=name, offset=base+offset, size=size,
                           sha256=hashlib.sha256(blob).hexdigest(), extracted=selected))
        if selected:
            destination = target/name
            if destination.exists() and destination.read_bytes() != blob:
                raise ValueError(f'Refusing to overwrite changed asset: {name}')
            destination.write_bytes(blob)
    manifest = dict(exe_name=exe.name, exe_size=len(data),
                    exe_sha256=hashlib.sha256(data).hexdigest(), archive_version=30,
                    archive_base=base, libraries=libraries, assets=assets)
    (target/'archive-index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('exe'); ap.add_argument('target')
    args=ap.parse_args(); m=extract(args.exe,args.target)
    print(json.dumps({'assets':len(m['assets']),'extracted':sum(a['extracted'] for a in m['assets']),'sha256':m['exe_sha256']}))
