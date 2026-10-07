from catalog import ROOT
from pathlib import Path
import io,pickle,zlib,shutil
class SafeIndex(pickle.Unpickler):
    def find_class(self,module,name):raise ValueError('Executable RPA index refused')
archive=Path(r'D:\software\steam\steamapps\common\oath\game\archive.rpa')
work=ROOT.parents[1]/'work/oath-parse'
with archive.open('rb') as f:
    h=f.readline().split();off=int(h[1],16);key=int(h[2],16);f.seek(off)
    index=SafeIndex(io.BytesIO(zlib.decompress(f.read()))).load()
    for mode in ['original','polished']:
        stage=work/mode/'game';stage.mkdir(parents=True,exist_ok=True)
        common=stage.parent/'engine-common'
        shutil.copytree(archive.parent.parent/'renpy/common',common,dirs_exist_ok=True)
        for p in (ROOT/'source').rglob('*.rpy'):
            rel=p.relative_to(ROOT/'source');changed=ROOT/'build/game'/rel
            selected=changed if mode=='polished' and changed.exists() else p
            target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(selected,target)
            name=rel.as_posix()+'c';entries=index.get(name,index.get(name.encode()))
            if entries:
                data=bytearray()
                for ent in entries:
                    start,size=ent[:2];f.seek(start^key);data.extend(ent[2] if len(ent)>2 else b'');data.extend(f.read(size^key))
                (stage/name).write_bytes(data)
        shutil.copyfile(archive.parent/'script_version.txt',stage/'script_version.txt')
print(work)
