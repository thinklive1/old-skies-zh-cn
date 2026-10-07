from catalog import ROOT,QUOTED
from apply_review import controls
import collections,hashlib,json,re,zipfile

def sha(data):return hashlib.sha256(data).hexdigest()

def repaired(text):
    return text.replace('{/字体}','{/font}').replace('{/颜色}','{/color}').replace('{/尺寸}','{/size}').replace('{size=*0。5}','{size=*0.5}').replace('[镇民]','[townpeople]').replace('[persistent。coins]','[persistent.coins]')

rows=json.loads((ROOT/'catalog.json').read_text('utf-8'))
if any(r['status']!='reviewed' for r in rows):raise SystemExit('Review incomplete')
groups=collections.defaultdict(list)
for r in rows:
    if r['target']!=r['original']:groups[r['file']].append(r)
files=[];changes=[]
for name,items in sorted(groups.items()):
    data=(ROOT/'source'/name).read_bytes();original=data.decode('utf-8');parts=[];mask=[];cursor=0
    for r in sorted(items,key=lambda r:r['start']):
        start,end=r['start'],r['end']
        if start<cursor or original[start:end]!=r['original']:raise ValueError('Bad literal span')
        if controls(repaired(r['original']))!=controls(repaired(r['target'])):raise ValueError('Text control changed '+str(r['id']))
        if re.search(r'(?<!\\)'+re.escape(r['quote']),r['target']) or '\n' in r['target'] or '\r' in r['target']:raise ValueError('Unsafe string boundary')
        parts.extend([original[cursor:start],r['target']]);mask.extend([original[cursor:start],'<HAN_TEXT>']);cursor=end
        changes.append(dict(id=r['id'],file=name,line=r['line'],english=r.get('english'),before=r['original'],after=r['target']))
    parts.append(original[cursor:]);mask.append(original[cursor:]);patched=''.join(parts);out=patched.encode('utf-8')
    # Independently reconstruct the untouched byte intervals from the output.
    at=0;check=[];original_at=0
    for r in sorted(items,key=lambda r:r['start']):
        prefix=original[original_at:r['start']]
        if patched[at:at+len(prefix)]!=prefix:raise ValueError('Code/prefix changed')
        check.extend([patched[at:at+len(prefix)],'<HAN_TEXT>']);at+=len(prefix)
        if patched[at:at+len(r['target'])]!=r['target']:raise ValueError('Wrong text payload')
        at+=len(r['target']);original_at=r['end']
    check.append(patched[at:])
    if ''.join(mask)!=''.join(check):raise ValueError('Non-text bytes changed')
    target=ROOT/'build/game'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(out)
    files.append(dict(path=name,before_sha256=sha(data),after_sha256=sha(out),size=len(out),changed_entries=len(items),
        outside_text_sha256=sha(''.join(mask).encode('utf-8')),outside_text_bytes_equal=True))
report=dict(version='1.1.0-rc.1',base_game_version='19-dlc-build_v17x_china_v8',
    scope_entries=len(rows),reviewed_entries=len(rows),changed_entries=len(changes),unchanged_entries=len(rows)-len(changes),
    files=files,changes_limited_to_existing_text_literals=True,game_logic_bytes_unchanged=True,
    markup_repairs={'{/字体}':'{/font}','{/颜色}':'{/color}','{/尺寸}':'{/size}','{size=*0。5}':'{size=*0.5}',
        '[镇民]':'[townpeople]','[persistent。coins]':'[persistent.coins]'},
    notes='Interpolation variables may be reordered within text, with identical names and occurrence counts. Only listed pre-existing translation damage is repaired.')
(ROOT/'review/text-only-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'review/changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
