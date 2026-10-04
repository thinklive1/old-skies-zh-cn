"""Compile a versioned AGS patch; never install or alter the game directory."""
import argparse,copy,hashlib,json,re,shutil,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY=b'Avis Durgan'
PRINTF=re.compile(r'%(?:\d+\$)?[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcspn%]')
VOICE=re.compile(r'^&\d+(?:\s|$)')
def decrypt(data):
    plain=bytes((x-KEY[i%11])%256 for i,x in enumerate(data))
    if not plain.endswith(b'\0'):raise ValueError('unterminated TRA string')
    return plain[:-1].decode('utf-8')
def encrypt(text):
    if '\0' in text:raise ValueError('embedded null')
    plain=text.encode('utf-8')+b'\0'
    encrypted=bytes((x+KEY[i%11])%256 for i,x in enumerate(plain))
    return struct.pack('<i',len(encrypted))+encrypted
def extract(blob):
    if blob[:15]!=b'AGSTranslation\0':raise ValueError('invalid AGS signature')
    offset=15
    while offset<len(blob):
        kind=struct.unpack_from('<i',blob,offset)[0]
        if kind<=0:raise ValueError('dictionary not found before extension/end block')
        size=struct.unpack_from('<i',blob,offset+4)[0];start=offset+8
        if kind==1:
            pos=start;records=[]
            while pos<start+size:
                pair=[]
                for _ in range(2):
                    length=struct.unpack_from('<i',blob,pos)[0];pos+=4
                    if length<1 or pos+length>start+size:raise ValueError('invalid string length')
                    pair.append(decrypt(blob[pos:pos+length]));pos+=length
                if pair==['','']:break
                records.append({'id':len(records),'en':pair[0],'zh':pair[1]})
            if pos!=start+size:raise ValueError('dictionary block size mismatch')
            return records,offset,start+size
        offset=start+size
    raise ValueError('dictionary absent')
def controls(s):
    m=VOICE.match(s)
    return {'voice':m.group(0).strip() if m else None,'printf':PRINTF.findall(s),'breaks':s.count('[')-s.count('\\['),'escapes':re.findall(r'\\[tnr]',s)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--candidate',action='store_true');parser.add_argument('--check-only',action='store_true');parser.add_argument('--build-tag',default='');args=parser.parse_args()
    if args.build_tag and not re.fullmatch(r'[a-zA-Z0-9_-]+',args.build_tag):raise SystemExit('Invalid build tag')
    original=json.loads((ROOT/'source/original.v1.0.json').read_text(encoding='utf-8'))
    edited=json.loads((ROOT/'source/translations.v1.1.json').read_text(encoding='utf-8'))
    project=json.loads((ROOT/'source/project.json').read_text(encoding='utf-8'))
    common=set(json.loads((ROOT/'source/font_common.json').read_text(encoding='utf-8')))
    original_chars=set(''.join(x['zh'] for x in original));errors=[];changes=[]
    policy_path=ROOT/'review/preserve_commentary.json'
    preserved=set(json.loads(policy_path.read_text(encoding='utf-8'))['ids']) if policy_path.exists() else set()
    if len(edited)!=len(original):errors.append('entry count changed')
    for a,b in zip(original,edited):
        if (a['id'],a['en'])!=(b['id'],b['en']):errors.append(f"{a['id']}: English key/order changed")
        if not isinstance(b['zh'],str) or not b['zh']:errors.append(f"{a['id']}: empty or invalid translation")
        if a['id'] in preserved and a['zh']!=b['zh']:errors.append(f"{a['id']}: excluded commentary differs from v1.0")
        if a['zh']==b['zh']:continue
        if controls(a['zh'])!=controls(b['zh']):errors.append(f"{a['id']}: control markers changed: {controls(a['zh'])} -> {controls(b['zh'])}")
        missing=sorted(set(b['zh'])-{chr(x) for x in common}-original_chars)
        missing=[c for c in missing if ord(c)>127]
        if missing:errors.append(f"{a['id']}: introduced unsupported glyphs: {''.join(missing)}")
        changes.append({'id':a['id'],'en':a['en'],'v1.0':a['zh'],'v1.1':b['zh'],'review_status':b.get('review_status','pending')})
    source=ROOT/'upstream/v1.0/PatchFiles/Chinese.tra';blob=source.read_bytes()
    if sha(source)!=project['original_tra_sha256']:errors.append('upstream TRA changed')
    parsed,start,end=extract(blob)
    if parsed!=original:errors.append('upstream extraction differs from locked original')
    dictionary=b''.join(encrypt(x['en'])+encrypt(x['zh']) for x in edited)+encrypt('')+encrypt('')
    compiled=blob[:start]+struct.pack('<ii',1,len(dictionary))+dictionary+blob[end:]
    roundtrip,rs,re_=extract(compiled)
    if roundtrip!=[{k:x[k] for k in ('id','en','zh')} for x in edited]:errors.append('compiled round-trip failed')
    if compiled[:start]!=blob[:start] or compiled[re_:]!=blob[end:]:errors.append('non-dictionary blocks changed')
    pending=sum(x.get('review_status')!='reviewed' for x in edited)
    report={'target_version':'1.1','stage':'candidate' if args.candidate else 'release_check','entries':len(edited),'changed_entries':len(changes),'reviewed_entries':len(edited)-pending,'pending_entries':pending,'technical_errors':errors,'technical_pass':not errors,'in_game_validation':'not_performed','release_ready':not errors and pending==0 and project.get('in_game_validation')=='passed'}
    report['preserved_commentary_entries']=len(preserved)
    report['preserved_commentary_pass']=all(edited[i]['zh']==original[i]['zh'] for i in preserved)
    report['in_game_validation_responsibility']=project.get('in_game_validation_responsibility','unassigned')
    (ROOT/'reports/qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'reports/changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit('Technical validation failed; no package created.')
    if args.check_only:return
    if not args.candidate and not report['release_ready']:raise SystemExit('Release blocked: full review and in-game validation required. Use --candidate for a clearly labeled review build.')
    label='OldSkies_往昔天穹_简体中文汉化_v1.1'+(('_候选版_首轮审校完成_待画面确认' if pending==0 else '_候选版_未完成全量审校') if args.candidate else '')
    if args.build_tag:label+='_'+args.build_tag
    dest=ROOT/'build'/label
    if dest.exists():raise SystemExit('Build directory exists; preserve prior builds and choose a new output directory before rebuilding.')
    shutil.copytree(ROOT/'upstream/v1.0',dest)
    (dest/'PatchFiles/Chinese.tra').write_bytes(compiled)
    manifest_path=dest/'patch_manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'));manifest['version']='1.1';manifest['revision_stage']='candidate' if args.candidate else 'release'
    for entry in manifest['files']:
        f=dest/'PatchFiles'/entry['name'];entry['sha256']=sha(f);entry['bytes']=f.stat().st_size
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    for name in ('安装汉化.ps1','卸载汉化.ps1'):
        f=dest/name;text=f.read_text(encoding='utf-8-sig');text=text.replace('$patchManifest.version -ne "1.0"','$patchManifest.version -ne "1.1"').replace('简体中文汉化 v1.0','简体中文汉化 v1.1');f.write_text(text,encoding='utf-8-sig')
    readme=dest/'安装说明.txt';text=readme.read_text(encoding='utf-8-sig');text=text.replace('简体中文汉化 v1.0','简体中文汉化 v1.1');text+='\n\nv1.1 文本修订说明\n----------------\n原 v1.0 汉化：那卡nakami。v1.1 为基于该版本的文本修订项目。\n'+f"本次修订 {len(changes)} 条；全包 {len(edited)} 条。\n"
    if args.candidate:text+=('本包已完成首轮全量文本核读，录音花絮和开发者解说保留 v1.0 原文。游戏画面与流程由用户确认，尚未记录游戏内验收通过。\n' if pending==0 else '本包为待审候选版：尚有未完成逐句审校的文本，且未进行游戏内排版与流程测试。\n')
    shutil.copy2(ROOT/'docs/CONTEXT_CHECKS.md',dest/'v1.1_语境回查记录.md')
    readme.write_text(text,encoding='utf-8-sig')
    shutil.copy2(ROOT/'reports/qa.json',dest/'v1.1_校验报告.json');shutil.copy2(ROOT/'reports/changes.json',dest/'v1.1_逐条修改记录.json')
    with zipfile.ZipFile(ROOT/'build'/(label+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for f in dest.rglob('*'):
            if f.is_file():z.write(f,f.relative_to(dest.parent))
    print('Created',dest)
if __name__=='__main__':main()
