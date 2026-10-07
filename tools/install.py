"""Install only the verified text overlay and its native compiled text cache."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,uuid,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'D:\software\steam\steamapps\common\oath')
NAMES=['battle/battle-screens.rpy','battle/battle-script.rpy','battle/battle-units.rpy','screens.rpy','script.rpy','tl/chinese/screens.rpy']
ALLOWED=set(NAMES+[x+'c' for x in NAMES])

def digest(path):
    if not path.is_file():return None
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def live_processes():
    result=subprocess.run(['powershell','-NoProfile','-Command',"Get-Process -Name oath -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],text=True,capture_output=True)
    return result.stdout.strip()
def install(dry_run=False):
    if live_processes():raise RuntimeError('Close oath before installing')
    if not (GAME/'oath.exe').is_file() or digest(GAME/'game/archive.rpa')!='5b7f80a9e943740540848248cb876cda017463f685a586ca321a5dea55b4fdcf':
        raise RuntimeError('Unsupported game/translation archive; refused to install')
    manifest=json.loads((ROOT/'review/text-only-verification.json').read_text('utf-8'))
    for name in NAMES:
        item=next(x for x in manifest['files'] if x['path']==name)
        if digest(ROOT/'build/game'/name)!=item['after_sha256']:raise RuntimeError('Stale text build')
    original=json.loads((ROOT/'review/engine-original.json').read_text('utf-8'))
    polished=json.loads((ROOT/'review/engine-polished.json').read_text('utf-8'))
    if not original['success'] or not polished['success'] or original['node_type_counts']!=polished['node_type_counts'] or original['branch_call_speaker_sha256']!=polished['branch_call_speaker_sha256']:
        raise RuntimeError('Native engine structure validation failed')
    scope={p.relative_to(GAME).as_posix():p for p in GAME.rglob('*') if p.is_file() and '_oath_zh_polish_backup' not in p.parts}
    untouched={name:digest(p) for name,p in scope.items() if name not in {'game/'+x for x in ALLOWED}}
    files=[]
    for name in sorted(ALLOWED):
        target=GAME/'game'/name;source=ROOT/'build/game'/name
        if not source.is_file():raise RuntimeError('Missing payload '+name)
        files.append(dict(path=name,before_sha256=digest(target),after_sha256=digest(source),size=source.stat().st_size))
    print(json.dumps(dict(game=str(GAME),files=files),ensure_ascii=False,indent=2),flush=True)
    if dry_run:return
    backup=GAME/'_oath_zh_polish_backup'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    backup.mkdir(parents=True)
    for item in files:
        target=GAME/'game'/item['path']
        if digest(target)!=item['before_sha256']:raise RuntimeError('Target changed during preflight')
        if item['before_sha256']:
            old=backup/'files'/item['path'];old.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,old)
            if digest(old)!=item['before_sha256']:raise RuntimeError('Backup mismatch')
    receipt=dict(game=str(GAME),version='1.1.0-rc.1',files=files,state='prepared',untouched_files=untouched)
    save(backup/'manifest.json',receipt);written=[]
    try:
        for item in files:
            target=GAME/'game'/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(target.name+'.oath-polish-tmp')
            if temp.exists():raise RuntimeError('Existing staging file')
            try:
                shutil.copyfile(ROOT/'build/game'/item['path'],temp)
                if digest(temp)!=item['after_sha256']:raise RuntimeError('Staging mismatch')
                temp.replace(target);written.append(item)
            finally:
                if temp.exists():temp.unlink()
        if any(digest(GAME/'game'/r['path'])!=r['after_sha256'] for r in files):raise RuntimeError('Installed payload mismatch')
        if any(digest(GAME/name)!=value for name,value in untouched.items()):raise RuntimeError('An unrelated game file changed')
    except Exception:
        for item in reversed(written):
            target=GAME/'game'/item['path']
            if item['before_sha256']:shutil.copyfile(backup/'files'/item['path'],target)
            elif digest(target)==item['after_sha256']:target.unlink()
        receipt['state']='failed-restored';save(backup/'manifest.json',receipt);raise
    receipt['state']='installed-verified';receipt['untouched_files_verified']=len(untouched)
    save(backup/'manifest.json',receipt)
    save(ROOT/'review/installation.json',dict(game=str(GAME),backup=str(backup),state=receipt['state'],
        payload_files_verified=len(files),untouched_files_verified=len(untouched),
        archive_sha256=untouched['game/archive.rpa'],saves_unchanged=all(digest(GAME/name)==value for name,value in untouched.items() if name.startswith('game/saves/'))))
    print('Installed and verified. Backup: '+str(backup),flush=True)
def rollback(backup):
    backup=Path(backup).resolve()
    if backup.parent!=GAME/'_oath_zh_polish_backup':raise RuntimeError('Unexpected backup location')
    receipt=json.loads((backup/'manifest.json').read_text('utf-8'))
    if receipt['game']!=str(GAME) or {x['path'] for x in receipt['files']}!=ALLOWED:raise RuntimeError('Unexpected backup scope')
    for r in receipt['files']:
        target=GAME/'game'/r['path']
        if digest(target) not in {r['before_sha256'],r['after_sha256']}:raise RuntimeError('Installed text was modified; review before rollback')
        if r['before_sha256'] and digest(backup/'files'/r['path'])!=r['before_sha256']:raise RuntimeError('Backup mismatch')
    for r in receipt['files']:
        target=GAME/'game'/r['path']
        if digest(target)==r['before_sha256']:continue
        if r['before_sha256']:shutil.copyfile(backup/'files'/r['path'],target)
        else:target.unlink()
    if any(digest(GAME/'game'/r['path'])!=r['before_sha256'] for r in receipt['files']):raise RuntimeError('Rollback mismatch')
    receipt['state']='rolled-back';save(backup/'manifest.json',receipt)
    print('Rollback verified')
if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    parser.add_argument('--game',default=str(GAME),help='Directory containing oath.exe')
    install_parser=sub.add_parser('install');install_parser.add_argument('--dry-run',action='store_true')
    roll=sub.add_parser('rollback');roll.add_argument('backup')
    args=parser.parse_args()
    GAME=Path(args.game).resolve()
    if args.command=='install':install(args.dry_run)
    else:rollback(args.backup)
