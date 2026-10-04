"""Apply explicit bilingual edits and their identical-English display variants."""
from pathlib import Path
import json,re,unicodedata,sys
ROOT=Path(__file__).resolve().parents[1]
def norm(text):
 text=re.sub(r'^(?:<[2bilr])+','',text)
 return re.sub(r'\s+',' ',text).strip()
def visual_width(text):
 return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .55 for c in text)
def wrap(text,limit):
 lines=[];current=''
 for c in text:
  if current and visual_width(current+c)>limit:
   if c in '，。！？：；、）》”’' and len(current)>1:
    lines.append(current[:-1]);current=current[-1:]+c
   else:lines.append(current);current=c
  else:current+=c
 if current:lines.append(current)
 return lines
def main():
 rows=json.loads((ROOT/'source/original.v1.0.1.json').read_text(encoding='utf-8'))
 direct={}
 for line in (ROOT/'source/manual_revisions.tsv').read_text(encoding='utf-8').splitlines():
  key,value=line.split('\t',1);key=int(key)
  if key in direct:raise ValueError(f'Duplicate edit: {key}')
  if not 0<=key<len(rows):raise ValueError(f'Bad ID: {key}')
  direct[key]=value
 mapping={}
 decisions=json.loads((ROOT/'source/revision_decisions.json').read_text(encoding='utf-8'))
 assert {d['id']:d['new_zh'] for d in decisions}==direct
 for d in decisions:assert rows[d['id']]['en']==d['expected_english'],('source key shifted',d['id'])
 for key,value in direct.items():
  en=norm(rows[key]['en']);zh=norm(value)
  if en in mapping and mapping[en][1]!=zh:raise ValueError(f'Conflicting variant: {en}')
  mapping[en]=(key,zh)
 corrections={10,14,15,579,584,691,729,784,791,826,847,852,860,909,988,989,1005,1056,1432,1764,2213,3408,4858,5981,6363,7367,7511,7993,8241,8955,9105,9524}
 edits=[]
 proof=json.loads((ROOT/'qa/full_review_coverage.json').read_text(encoding='utf-8'))
 reviewed=set(proof['reviewed_ids']);numeric=set(proof['numeric_ids'])
 assert reviewed|numeric==set(range(len(rows))) and not reviewed&numeric
 for key in numeric:
  assert re.fullmatch(r'\d+ Pesos',norm(rows[key]['en']))
  assert norm(rows[key]['zh'])==norm(rows[key]['en']).split()[0]+' 比索'
 master=[]
 for r in rows:
  key=r['id'];value=r['zh'];link=None
  if key in direct:value=direct[key];link=key
  elif norm(r['en']) in mapping:
   link,newbody=mapping[norm(r['en'])]
   prefix=re.match(r'^(?:<[2bilr])+\s*',r['zh'])
   value=(prefix.group() if prefix else '')+newbody
  status='reviewed_unchanged' if key in reviewed else 'numeric_verified_unchanged'
  if value!=r['zh']:
   status='edited_direct' if key==link else 'edited_same_english_variant'
   edits.append({'id':key,'en':r['en'],'before':r['zh'],'after':value,'basis_id':link,'reason':'修正误译或不准确表达' if link in corrections else '改善中文表达与角色语气'})
  master.append({**r,'original_zh':r['zh'],'zh':value,'status':status,'basis_id':link})
 # Sync already-split journal paragraphs by exact original Chinese concatenation.
 diary=[r for r in master if r['en'].startswith('RES_JOURNAL_LINE_')]
 journal_matches=[]
 for r in rows:
  if not r['en'].startswith('*') or r['id'] not in direct:continue
  old=r['zh'].removeprefix('*');new=direct[r['id']].removeprefix('*')
  for i in range(len(diary)):
   accum=''
   for j in range(i,len(diary)):
    accum+=diary[j]['original_zh']
    if accum==old:
     group=diary[i:j+1];limit=max(visual_width(x['original_zh']) for x in group)
     pieces=wrap(new,limit)
     if len(pieces)>len(group):raise ValueError(f'Journal overflow: {r["id"]} needs {len(pieces)} lines, has {len(group)}')
     for k,item in enumerate(group):
      value=pieces[k] if k<len(pieces) else ' '
      if value!=item['original_zh']:
       edits.append({'id':item['id'],'en':item['en'],'before':item['original_zh'],'after':value,'basis_id':r['id'],'reason':'同步日记分行显示，保留行数、日期与分页'})
       item['zh']=value;item['status']='edited_journal_line';item['basis_id']=r['id']
     assert ''.join(x['zh'] for x in group).rstrip()==new
     journal_matches.append({'basis_id':r['id'],'first':group[0]['id'],'last':group[-1]['id'],'width_limit_units':limit,'used_lines':len(pieces),'slots':len(group)})
     break
    if not old.startswith(accum):break
   else:continue
   if accum==old:break
  else:raise ValueError(f'Journal original paragraph missing: {r["id"]}')
 (ROOT/'source/translations.v1.1.json').write_text(json.dumps(master,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'source/change_log.json').write_text(json.dumps(edits,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'qa/journal_sync.json').write_text(json.dumps(journal_matches,ensure_ascii=False,indent=2),encoding='utf-8')
 from collections import Counter
 print(json.dumps(dict(Counter(r['status'] for r in master)),ensure_ascii=False));print('Changed rows:',len(edits),'manual decisions:',len(direct),'journal paragraphs:',len(journal_matches))
if __name__=='__main__':main()
