from catalog import ROOT,source_text,QUOTED
import json,re,collections

rows=json.loads((ROOT/'catalog.json').read_text('utf-8'))
base=collections.defaultdict(list);english=collections.defaultdict(list)
label=''
main_lines=source_text(ROOT/'source/script.rpy').splitlines()
for number,line in enumerate(main_lines,1):
    m=re.match(r'^label\s+([^:]+):',line)
    if m:label=m[1]
    m=re.match(r'^\s+([A-Za-z_][A-Za-z_0-9]*)\s+("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')\s*$',line)
    if m and m[1] not in {'play','queue','scene','show','hide','image','jump','call','return','text','textbutton','label','tooltip','old','new'}:
        next_line=next((s for s in main_lines[number:] if s.strip()),'')
        if re.match(r'^\s*["\']',next_line) and next_line.rstrip().endswith(':'):
            continue # Ren'Py menu captions are translated as strings rather than say blocks.
        base[label].append((number,m[1],m[2][1:-1]))
label=''
for line in source_text(ROOT/'source/tl/chinese/script.rpy').splitlines():
    m=re.match(r'^translate chinese (.+)_[0-9a-f]{8}(?:_\d+)?:',line)
    if m:label=m[1]
    m=re.match(r'^\s+# ([A-Za-z_][A-Za-z_0-9]*)\s+("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')\s*$',line)
    if m:english[label].append((m[1],m[2][1:-1]))
aligned={};mismatched=[]
for label,sequence in base.items():
    other=english[label]
    if len(sequence)==len(other) and [x[1] for x in sequence]==[x[0] for x in other]:
        for a,b in zip(sequence,other):aligned[a[0]]=b[1]
    elif other:mismatched.append((label,len(sequence),len(other)))
for row in rows:
    if row['file']=='script.rpy':
        if 'english_line_hint' not in row:row['english_line_hint']=row.get('english')
        row['english']=aligned.get(row['line'])
        row['english_alignment']='label-dialogue-count-and-speaker-match' if row['english'] is not None else 'unconfirmed'
    elif row['file'].endswith('screens.rpy'):
        if 'english_line_hint' not in row:row['english_line_hint']=row.get('english')
        row['english']=None
        row['english_alignment']='unconfirmed-line-offset'
(ROOT/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'review').mkdir(exist_ok=True)
(ROOT/'review/alignment.json').write_text(json.dumps(dict(aligned_lines=len(aligned),mismatched_labels=mismatched),ensure_ascii=False,indent=2),encoding='utf-8')
print('Aligned dialogue lines',len(aligned),'mismatched labels',len(mismatched),'confirmed Chinese entries',sum(r['english'] is not None for r in rows))
print(mismatched[:25])
