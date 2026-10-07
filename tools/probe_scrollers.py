"""Execute translation detours in a marked private game copy, then restore.

This injects a temporary game_start probe that aborts with inspected list items.
It does not play the story, touch real saves, or form part of a release payload.
"""
import argparse, contextlib, hashlib, io, os, struct, subprocess, uuid
from pathlib import Path
from catalog import ROOT, read_json, write_json
from install import install, rollback, digest
from scom_runtime import parse, serialize, translate_scrollers


def find_scripts(data):
    found=[]; pos=0
    while True:
        offset=data.find(b'SCOM',pos)
        if offset<0: break
        try: script=parse(data,offset)
        except (ValueError,UnicodeError,struct.error):
            pos=offset+4;continue
        found.append(script);pos=script['end']
    return found


def add_probe(script, table):
    code=script['code'].copy(); imports=script['imports'].copy();fixups=script['fixups'].copy()
    strings=bytearray(script['strings']);op={i['name']:i['opcode'] for i in table}
    def symbol(name):
        if name not in imports: imports[imports.index('')]=name
        return imports.index(name)
    def emit(name,*args):
        code.extend([op[name],*args])
    def imported(reg,name):
        fixups.append((4,len(code)+2));emit('movlit',reg,symbol(name))
    def literal(text):
        offset=len(strings);strings.extend(text.encode('cp1252')+b'\0')
        fixups.append((3,len(code)+2));emit('movlit',3,offset)
    def call(name,n):
        emit('setfuncargs',n);imported(3,name);emit('callext',3);emit('subreal',n)
    def set_global(name,text):
        literal(text);emit('newstr',3);imported(2,name);emit('memwriteptr',3)
    def item(list_name,index):
        emit('movlit',3,index);emit('pushreal',3)
        imported(2,list_name);emit('movreg',2,3);emit('thisptr',3)
        call('ListBox::geti_Items',1)
    helper=len(code)
    if code[:2]!=[op['sourceline'],54]:raise ValueError('Unexpected game_start entry')
    code[:2]=[op['jmp'],helper-2];emit('baseptr',0)
    set_global('ScrollText1','Speech Volume');set_global('ScrollText2','Save Game')
    set_global('ScrollText3','Latest Sports');set_global('ScrollText4','Forecast')
    emit('movlit',3,26);emit('pushreal',3)
    imported(2,'ListNewsArticle');emit('movreg',2,3);emit('pushreal',3)
    call('MakeScrollList',2)
    item('ListNewsArticle',0);imported(2,'ScrollText2');emit('memwriteptr',3)
    # Arguments are pushed in reverse order: body, subject, date, sender.
    for text in [
        'A green, recyclable plastic tray, the kind the food machine serves its slop in.',
        'Save Game','08 July 2087','Dr Nina Jeong']:
        literal(text);emit('newstr',3);emit('pushreal',3)
    call('MakeEmail',4)
    item('ListBoxEmailMessage1',9);imported(2,'ScrollText3');emit('memwriteptr',3)
    item('ListBoxEmailMessage1',5);imported(2,'ScrollText4');emit('memwriteptr',3)
    for field in ['ScrollText4','ScrollText3','ScrollText2']:
        imported(2,field);emit('memreadptr',3);emit('pushreal',3)
    literal('TB_L10N_PROBE news:%s mail:%s subject:%s');emit('pushreal',3)
    call('AbortGame',4);emit('ret')
    return serialize({**script,'code':code,'imports':imports,'fixups':fixups,'strings':bytes(strings)})


def probe(game,metadata,release=False):
    game=Path(game).resolve();marker=read_json(game/'.technobabylon-test-copy.json')
    if marker.get('isolated_copy') is not True or marker.get('exe_sha256')!=digest(game/'Technobabylon.exe'):
        raise ValueError('Private-copy marker mismatch')
    meta=read_json(metadata);table=meta['instructions']
    manifest=read_json(ROOT/'build'/('release' if release else 'development')/'build-manifest.json')
    names=[f['name'] for f in manifest['files']]+['acsetup.cfg']
    before={n:digest(game/n) for n in names}
    backup=None;process=None;record={'passed':False,'isolated_copy':True,'visual_test':False}
    run=game/('scrollers-probe-'+uuid.uuid4().hex[:8])
    for d in ['userdata','shared','logs']:(run/d).mkdir(parents=True,exist_ok=True)
    try:
        with contextlib.redirect_stdout(io.StringIO()):backup=install(game,not release)
        data=(game/'game28.dta').read_bytes();scripts=find_scripts(data);replacements=[]
        installed_hook=read_json(ROOT/'source/runtime-keys.json').get('scroller_hook')
        found_scroller=False
        for s in scripts:
            sections=[x['name'] for x in s['sections']]
            if sections==['Scrollers.asc']:
                blob=data[s['offset']:s['end']]
                found_scroller=True
                if installed_hook and hashlib.sha256(blob).hexdigest()==installed_hook['patched_sha256']:
                    record['detour']=installed_hook['report']
                    record['hook_source']='installed candidate payload'
                else:
                    patched,report=translate_scrollers(blob,table)
                    record['detour']=report;replacements.append((s['offset'],s['end'],patched))
                    record['hook_source']='temporary prototype module'
            elif sections==['GlobalScript.asc']:
                replacements.append((s['offset'],s['end'],add_probe(s,table)))
        if not found_scroller or len(replacements) not in [1,2]:
            raise ValueError('Did not find selected runtime/probe scripts')
        for start,end,blob in sorted(replacements,reverse=True):data=data[:start]+blob+data[end:]
        (run/'probe-game28.dta').write_bytes(data);(game/'game28.dta').write_bytes(data)
        args=[str(game/'Technobabylon.exe'),'--localuserconf','--windowed','--gfxdriver','Software',
              '--no-message-box','--log-file=all:debug','--log-file-path='+str(run/'logs'),
              '--user-data-dir',str(run/'userdata'),'--shared-data-dir',str(run/'shared')]
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'}
        with (run/'stdout.txt').open('wb') as out,(run/'stderr.txt').open('wb') as err:
            process=subprocess.Popen(args,cwd=game,env=env,stdout=out,stderr=err,startupinfo=startup)
            try: process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
        log=(run/'logs/ags.log').read_text('utf-8',errors='replace')
        (ROOT/'review/qa/scrollers-probe.log').write_text(log,encoding='utf-8')
        record['log_tail']=log[-5000:];record['exit_code']=process.returncode
        record['passed']='TB_L10N_PROBE news:语音音量' in log and 'mail:绿色的可回收塑料托盘' in log and 'subject:保存游戏' in log
    except Exception as error:record['error']=str(error)
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=10)
        if backup:
            # The temporary probe data intentionally differs from the installed payload.
            # Restore that one file to the installed hash before normal guarded rollback.
            original_payload=ROOT/'build'/('release' if release else 'development')/'game28.dta'
            (game/'game28.dta').write_bytes(original_payload.read_bytes())
            with contextlib.redirect_stdout(io.StringIO()):rollback(backup)
        record['rollback_byte_exact']=before=={n:digest(game/n) for n in names}
        record['passed']=record['passed'] and record['rollback_byte_exact']
        write_json(ROOT/'review/qa/scrollers-probe.json',record)
    print('Scroller translation execution/rollback: '+('passed' if record['passed'] else 'FAILED'))
    if not record['passed']:print(record.get('error',record.get('log_tail','')))
    return record['passed']


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('private_copy');ap.add_argument('metadata');ap.add_argument('--release',action='store_true');a=ap.parse_args()
    raise SystemExit(0 if probe(a.private_copy,a.metadata,a.release) else 1)
