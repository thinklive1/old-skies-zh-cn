"""Verified installation, preflight plan, byte-exact backups and guarded rollback."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,shutil,uuid
from catalog import ROOT,read_json,write_json

def digest(path):
    if not Path(path).is_file():return None
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def language_config(data,name):
    # The supplied original is ASCII/CP1252. Keep all unrelated bytes and line
    # endings intact; only alter the translation entry in [language].
    text=data.decode('cp1252');nl='\r\n' if '\r\n' in text else '\n'
    sections=list(re.finditer(r'(?im)^\[([^\]\r\n]+)\][ \t]*\r?$',text))
    lang=[(i,m) for i,m in enumerate(sections) if m[1].lower()=='language']
    if len(lang)>1:raise ValueError('Duplicate [language] sections')
    if not lang:
        return (text.rstrip('\r\n')+nl+'[language]'+nl+'translation='+name+nl).encode('cp1252')
    i,m=lang[0];start=m.end();end=sections[i+1].start() if i+1<len(sections) else len(text)
    part=text[start:end]
    keys=list(re.finditer(r'(?im)^translation[ \t]*=[^\r\n]*',part))
    if len(keys)>1:raise ValueError('Duplicate translation settings')
    if keys:
        k=keys[0];part=part[:k.start()]+'translation='+name+part[k.end():]
    else:part=nl+'translation='+name+nl+part.lstrip('\r\n')
    return (text[:start]+part+text[end:]).encode('cp1252')

def plan(game,development=False):
    game=Path(game).resolve();build=ROOT/'build'/('development' if development else 'release')
    manifest=read_json(build/'build-manifest.json');cfg=read_json(ROOT/'project.json')
    if manifest['development']!=development:raise ValueError('Build type mismatch')
    if not development and not manifest['complete']:raise ValueError('Incomplete release')
    if digest(game/'Technobabylon.exe')!=manifest['exe_sha256']:raise ValueError('Unsupported game executable; refused to install')
    required={cfg['translation_name']+'.tra'}|{f'agsfnt{i}.ttf' for i in range(8)}
    if manifest.get('context_data_required'):
        spec=read_json(ROOT/'source/runtime-keys.json')
        if spec['asset_name']!='game28.dta':raise ValueError('Unexpected context data filename')
        context=manifest.get('context_data',{})
        if context.get('patched_sha256')!=spec['patched_sha256'] or context.get('source_sha256')!=spec['source_sha256']:
            raise ValueError('Context data build missing or stale')
        if digest(game/'game28.dta') not in {None,spec['source_sha256'],spec['patched_sha256']}:
            raise ValueError('Unsupported external game data; refused to overwrite')
        required.add('game28.dta')
    items=[];seen=set()
    for r in manifest['files']:
        name=r['name']
        if name not in required or name in seen:raise ValueError('Unexpected or repeated install filename')
        seen.add(name);source=build/name
        if digest(source)!=r['sha256']:raise ValueError('Build file checksum mismatch: '+name)
        if name=='game28.dta' and r['sha256']!=spec['patched_sha256']:raise ValueError('Unexpected patched game data checksum')
        items.append(dict(name=name,source=str(source),before=digest(game/name),after=r['sha256']))
    if seen!=required:raise ValueError('Font/translation/context build incomplete')
    config=game/'acsetup.cfg'
    if not config.is_file():raise ValueError('Missing acsetup.cfg')
    modified=language_config(config.read_bytes(),cfg['translation_name'])
    items.append(dict(name='acsetup.cfg',source=None,before=digest(config),after=hashlib.sha256(modified).hexdigest()))
    return game,manifest,items,modified

def install(game,development=False,dry_run=False):
    game,manifest,items,modified=plan(game,development)
    print(json.dumps(dict(game=str(game),development=development,files=items),ensure_ascii=False,indent=2))
    if dry_run:return None
    backup=game/'_Technobabylon_zh_CN_backup'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    backup.mkdir(parents=True)
    for r in items:
        target=game/r['name']
        if digest(target)!=r['before']:raise ValueError('Game changed during preflight')
        if r['before']:
            shutil.copy2(target,backup/r['name'])
            if digest(backup/r['name'])!=r['before']:raise ValueError('Backup verification failed')
    record=dict(game=str(game),version=manifest['version'],development=development,state='prepared',files=items)
    write_json(backup/'backup-manifest.json',record)
    # Roll back only files we changed if the install fails midway.
    installed=[]
    try:
        for r in items:
            target=game/r['name'];staging=game/(r['name']+'.technobabylon-tmp')
            if staging.exists():raise ValueError('Existing staging file; inspect before retry')
            try:
                if r['source']:shutil.copyfile(r['source'],staging)
                else:staging.write_bytes(modified)
                if digest(staging)!=r['after']:raise ValueError('Staging checksum mismatch')
                staging.replace(target);installed.append(r)
            finally:
                if staging.exists():staging.unlink()
        for r in items:
            if digest(game/r['name'])!=r['after']:raise ValueError('Installed checksum mismatch')
    except Exception:
        for r in reversed(installed):
            if r['before']:shutil.copyfile(backup/r['name'],game/r['name'])
            elif digest(game/r['name'])==r['after']:(game/r['name']).unlink()
        record['state']='failed-restored';write_json(backup/'backup-manifest.json',record);raise
    record['state']='installed-verified';write_json(backup/'backup-manifest.json',record)
    print('Installed and verified. Backup: '+str(backup));return backup

def rollback(backup):
    backup=Path(backup).resolve();record=read_json(backup/'backup-manifest.json');game=Path(record['game']).resolve()
    if backup.parent!=game/'_Technobabylon_zh_CN_backup':raise ValueError('Backup location mismatch')
    # Rollback is independent of the current project build and Steam version.
    # Restore the exact old nine-payload or new ten-payload receipt, independent
    # of the current build. Never accept arbitrary extra names or duplicates.
    allowed={'Technobabylon_zh_CN.tra','acsetup.cfg'}|{f'agsfnt{i}.ttf' for i in range(8)}
    names={r['name'] for r in record['files']}
    if names not in (allowed,allowed|{'game28.dta'}) or len(record['files'])!=len(names):raise ValueError('Unexpected backup file list')
    for r in record['files']:
        if digest(game/r['name']) not in {r['after'],r['before']}:raise ValueError('Installed file was changed; manual review needed: '+r['name'])
        if r['before'] and digest(backup/r['name'])!=r['before']:raise ValueError('Backup checksum mismatch')
    for r in record['files']:
        target=game/r['name']
        if digest(target)==r['before']:continue
        if r['before']:
            staging=game/(r['name']+'.rollback-'+uuid.uuid4().hex)
            shutil.copyfile(backup/r['name'],staging);staging.replace(target)
        else:target.unlink()
    for r in record['files']:
        if digest(game/r['name'])!=r['before']:raise ValueError('Rollback verification failed')
    record['state']='rolled-back-verified';write_json(backup/'backup-manifest.json',record);print('Rollback verified')

if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    i=sub.add_parser('install');i.add_argument('game');i.add_argument('--development',action='store_true');i.add_argument('--dry-run',action='store_true')
    r=sub.add_parser('rollback');r.add_argument('backup');a=ap.parse_args()
    if a.command=='install':install(a.game,a.development,a.dry_run)
    else:rollback(a.backup)
