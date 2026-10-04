"""Import a user-downloaded patch ZIP as local build dependencies; no network calls."""
import argparse, hashlib, json, shutil, struct, zipfile
from pathlib import Path, PurePosixPath
import build

ROOT = Path(__file__).resolve().parents[1]

def prepare(package, dest):
    if dest.exists():
        raise ValueError('Dependency directory exists; keep it and choose a new --dest.')
    original = json.loads((ROOT/'source/original.v1.0.json').read_text(encoding='utf-8'))
    project = json.loads((ROOT/'source/project.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(package) as z:
        manifests = [n for n in z.namelist() if n.endswith('patch_manifest.json')]
        if len(manifests) != 1:
            raise ValueError('Expected one patch manifest in the ZIP.')
        prefix = manifests[0][:-len('patch_manifest.json')]
        manifest = json.loads(z.read(manifests[0]).decode('utf-8-sig'))
        blob = z.read(prefix+'PatchFiles/Chinese.tra')
        records, start, end = build.extract(blob)
        if [(x['id'],x['en']) for x in records] != [(x['id'],x['en']) for x in original]:
            raise ValueError('Patch English keys differ from the locked source.')
        dictionary = b''.join(build.encrypt(x['en'])+build.encrypt(x['zh']) for x in original)
        dictionary += build.encrypt('')+build.encrypt('')
        restored = blob[:start]+struct.pack('<ii',1,len(dictionary))+dictionary+blob[end:]
        if hashlib.sha256(restored).hexdigest() != project['original_tra_sha256']:
            raise ValueError('Reconstructed v1.0 TRA hash does not match.')
        for entry in manifest['files']:
            content=z.read(prefix+'PatchFiles/'+entry['name'])
            if hashlib.sha256(content).hexdigest()!=entry['sha256']:
                raise ValueError('Patch file hash differs: '+entry['name'])
        for entry in manifest['sprites']:
            content=z.read(prefix+'SpriteData/'+entry['bin'])
            if hashlib.sha256(content).hexdigest()!=entry['sha256_new']:
                raise ValueError('Sprite hash differs: '+entry['bin'])
        members=[]
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(prefix):
                continue
            rel=PurePosixPath(info.filename[len(prefix):])
            if rel.is_absolute() or '..' in rel.parts or '\\' in str(rel) or ':' in str(rel):
                raise ValueError('Unsafe ZIP member path.')
            members.append((info,rel))
        dest.mkdir(parents=True)
        for info,rel in members:
            target=dest.joinpath(*rel.parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(info) as source,target.open('wb') as output:
                shutil.copyfileobj(source,output)
    (dest/'PatchFiles/Chinese.tra').write_bytes(restored)
    manifest['version']='1.0'
    for entry in manifest['files']:
        if entry['name']=='Chinese.tra':
            entry['sha256']=project['original_tra_sha256']
            entry['bytes']=len(restored)
    (dest/'patch_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    for name in ['安装汉化.ps1','卸载汉化.ps1']:
        path=dest/name
        text=path.read_text(encoding='utf-8-sig').replace('$patchManifest.version -ne "1.1"','$patchManifest.version -ne "1.0"').replace('简体中文汉化 v1.1','简体中文汉化 v1.0')
        path.write_text(text,encoding='utf-8-sig')
    print('Imported dependencies; locked v1.0 TRA SHA256 verified:',dest)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--patch-zip',type=Path,required=True)
    parser.add_argument('--dest',type=Path,default=ROOT/'upstream/v1.0')
    args=parser.parse_args()
    prepare(args.patch_zip,args.dest)
