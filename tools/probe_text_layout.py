"""Private-copy engine checks: every long catalog paragraph and font-3 GUI label.

Temporary game_start code measures real AGS widths and character preservation;
it is removed before the normal guarded rollback. No visible/gameplay test.
"""
import argparse, contextlib, hashlib, io, os, subprocess, uuid
from pathlib import Path
from catalog import ROOT, read_json, write_json, load
from install import install, rollback, digest
from probe_scrollers import find_scripts
from scom_runtime import serialize


def injected(script, table, cases, controls):
    code=script['code'].copy();imports=script['imports'].copy();fixups=script['fixups'].copy()
    strings=bytearray(script['strings']);op={i['name']:i['opcode'] for i in table};stack=0;labels={};branches=[]
    def emit(name,*args):
        nonlocal stack
        code.extend([op[name],*args])
        if name=='push':stack+=4
        elif name=='pop':stack-=4
        elif name=='add' and args[0]==1:stack+=args[1]
        elif name=='sub' and args[0]==1:stack-=args[1]
    def imported(reg,name):
        if name not in imports:imports[imports.index('')]=name
        fixups.append((4,len(code)+2));emit('movlit',reg,imports.index(name))
    def native(name,n):
        emit('setfuncargs',n);imported(3,name);emit('callext',3)
        if n:emit('subreal',n)
    def literal(text):
        pos=len(strings);strings.extend(text.encode('cp1252')+b'\0');fixups.append((3,len(code)+2));emit('movlit',3,pos)
    def arg(off,ptr=True):emit('loadspoffs',off+stack);emit('memreadptr' if ptr else 'memread',3)
    def local(i):emit('loadspoffs',stack-4*i);emit('memread',3)
    def store(i):emit('loadspoffs',stack-4*i);emit('memwrite',3)
    def jump(label,kind='jmp'):branches.append((len(code)+1,label));emit(kind,0)
    def mark(label):labels[label]=len(code)
    def member(name,obj,argument=None):
        emit('push',6)
        if argument:argument();emit('pushreal',3)
        obj();emit('thisptr',3);native(name,1 if argument else 0);emit('pop',6)
    def item():member('ListBox::geti_Items',lambda:arg(8),lambda:local(0))
    def fail(message):literal(message);emit('pushreal',3);native('AbortGame',1)
    # validate(list, expected total character count), returns widest item.
    helper=len(code);emit('baseptr',helper);arg(8,False);emit('loadspoffs',8);emit('meminitptr',3)
    for i in range(5):
        if i==1:member('ListBox::get_ItemCount',lambda:arg(8))
        else:emit('movlit',3,0)
        emit('movreg',1,2);emit('memwrite',3);emit('add',1,4)
    mark('loop');local(0);emit('push',3);local(1);emit('pop',4);emit('le',4,3);emit('movreg',4,3);jump('end','jz')
    member('String::get_Length',item);emit('push',3);local(2);emit('pop',4);emit('addreg',4,3);emit('movreg',4,3);store(2)
    emit('movlit',3,0);emit('pushreal',3);item();emit('pushreal',3);native('GetTextWidth',2);store(4)
    emit('push',3);emit('movlit',3,260);emit('pop',4);emit('gr',4,3);emit('movreg',4,3);jump('width-ok','jz')
    fail('TB_LAYOUT_FAIL line wider than 260 pixels')
    mark('width-ok');local(4);emit('push',3);local(3);emit('pop',4);emit('gr',4,3);emit('movreg',4,3);jump('max-ok','jz');local(4);store(3)
    mark('max-ok');local(0);emit('add',3,1);store(0);jump('loop')
    mark('end');local(2);emit('push',3);arg(12,False);emit('pop',4);emit('eq',4,3);emit('movreg',4,3);jump('chars-ok','jnz')
    fail('TB_LAYOUT_FAIL character count differs')
    mark('chars-ok');local(3);emit('sub',1,20);emit('loadspoffs',8);emit('memzeroptrnd');emit('ret')
    if stack:raise ValueError('Validator stack imbalance')
    entry=len(code)
    if code[:2]!=[op['sourceline'],54]:raise ValueError('Unexpected game_start')
    code[:2]=[op['jmp'],entry-2];emit('baseptr',0)
    def named(name):imported(2,name);emit('movreg',2,3)
    def set_global(name,text):literal(text);emit('newstr',3);imported(2,name);emit('memwriteptr',3)
    def validate(list_name,count,index):
        emit('movlit',3,count);emit('push',3);named(list_name);emit('push',3)
        fixups.append((2,len(code)+2));emit('movlit',3,helper);emit('call',3);emit('sub',1,8)
    _,rows,_=load();mapping={r['source']:r['target'] for r in rows.values() if r['status'] in ['reviewed','preserve']}
    header=sum(len(mapping.get(s,s)) for s in ['FROM:','RECEIVED:','SUBJECT:'])+3*len(mapping['Save Game'])+20+5
    for index,r in enumerate(cases):
        set_global('ScrollText1',r['source'])
        for field in ['ScrollText2','ScrollText3','ScrollText4']:set_global(field,'')
        emit('movlit',3,26);emit('pushreal',3);named('ListNewsArticle');emit('pushreal',3);native('MakeScrollList',2)
        count=len(r['target'].replace('[',''));validate('ListNewsArticle',count,index*2)
        for text in [r['source'],'Save Game','Save Game','Save Game']:literal(text);emit('newstr',3);emit('pushreal',3)
        native('MakeEmail',4);validate('ListBoxEmailMessage1',count+header,index*2+1)
    for index,c in enumerate(controls):
        emit('movlit',3,3);emit('pushreal',3);literal(c['text']);emit('pushreal',3);native('GetTranslation',1);emit('pushreal',3);native('GetTextWidth',2)
        emit('push',3);emit('movlit',3,c['width']);emit('pop',4);emit('gr',4,3);emit('movreg',4,3);jump('control-'+str(index),'jz')
        fail('TB_LAYOUT_FAIL font3 '+c['name']);mark('control-'+str(index))
    literal(f'TB_LAYOUT_PASS paragraphs:{len(cases)} list_checks:{len(cases)*2} font3_controls:{len(controls)} all_lines_le_260px character_counts_preserved')
    emit('pushreal',3);native('AbortGame',1);emit('ret')
    for pos,label in branches:code[pos]=labels[label]-pos-1
    return serialize({**script,'code':code,'imports':imports,'fixups':fixups,'strings':bytes(strings)})


def run(game,metadata,release=False):
    game=Path(game).resolve();marker=read_json(game/'.technobabylon-test-copy.json')
    if marker.get('isolated_copy') is not True or marker.get('exe_sha256')!=digest(game/'Technobabylon.exe'):raise ValueError('Private copy required')
    meta=read_json(metadata);_,rows,_=load()
    cases=[r for r in rows.values() if r['status']=='reviewed' and len(r['source'])>90 and not r['source'].startswith('&')]
    controls=[c for c in meta['labels']+meta['buttons'] if c['font']==3 and c.get('text')]
    manifest=read_json(ROOT/'build'/('release' if release else 'development')/'build-manifest.json');names=[f['name'] for f in manifest['files']]+['acsetup.cfg'];before={n:digest(game/n) for n in names}
    record=dict(passed=False,isolated_copy=True,visual_game_verified=False,paragraph_ids=[r['id'] for r in cases],font3_controls=[c['name'] for c in controls],build_files=manifest['files'])
    folder=game/('layout-probe-'+uuid.uuid4().hex[:8]);folder.mkdir()
    for n in ['userdata','shared','logs']:(folder/n).mkdir()
    backup=None;process=None
    try:
        with contextlib.redirect_stdout(io.StringIO()):backup=install(game,not release)
        data=(game/'game28.dta').read_bytes();script=next(s for s in find_scripts(data) if s['sections']==[dict(name='GlobalScript.asc',offset=0)])
        payload=injected(script,meta['instructions'],cases,controls);data=data[:script['offset']]+payload+data[script['end']:];(game/'game28.dta').write_bytes(data)
        args=[str(game/'Technobabylon.exe'),'--localuserconf','--windowed','--gfxdriver','Software','--no-message-box','--log-file=all:debug','--log-file-path='+str(folder/'logs'),'--user-data-dir',str(folder/'userdata'),'--shared-data-dir',str(folder/'shared')]
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        with (folder/'stdout.txt').open('wb') as out,(folder/'stderr.txt').open('wb') as err:
            process=subprocess.Popen(args,cwd=game,env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'},stdout=out,stderr=err,startupinfo=startup)
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=10)
        log=(folder/'logs/ags.log').read_text('utf-8',errors='replace');(ROOT/'review/qa/text-layout-probe.log').write_text(log,encoding='utf-8');record['log_tail']=log[-3500:];record['passed']='TB_LAYOUT_PASS paragraphs:' in log and 'TB_LAYOUT_FAIL' not in log;record['exit_code']=process.returncode
    except Exception as error:record['error']=str(error)
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=10)
        if backup:
            (game/'game28.dta').write_bytes((ROOT/'build'/('release' if release else 'development')/'game28.dta').read_bytes())
            with contextlib.redirect_stdout(io.StringIO()):rollback(backup)
        record['rollback_byte_exact']=before=={n:digest(game/n) for n in names};record['passed']=record['passed'] and record['rollback_byte_exact'];write_json(ROOT/'review/qa/text-layout-probe.json',record)
    print('Engine text layout: '+('passed' if record['passed'] else 'FAILED'))
    if not record['passed']:print(record.get('error',record.get('log_tail','')))
    return record['passed']


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('private_copy');ap.add_argument('metadata');ap.add_argument('--release',action='store_true');a=ap.parse_args();raise SystemExit(0 if run(a.private_copy,a.metadata,a.release) else 1)
