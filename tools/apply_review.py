from catalog import ROOT
import json,re,sys,hashlib

def controls(text):
    return (sorted(re.findall(r'\[[^\]\r\n]*\]',text)),
        re.findall(r'\{[^}\r\n]*\}|\\(?:[nrt"\'\\]|u[0-9a-fA-F]{4})',text),text.count('\\'))

def apply(name,changes,review_ids=None,allow_tag_repair=False):
    rows=json.loads((ROOT/'catalog.json').read_text('utf-8'));before={}
    for key,value in changes.items():
        row=rows[int(key)];old=row['target']
        if controls(old)!=controls(value):
            repaired=old.replace('{/字体}','{/font}').replace('{/颜色}','{/color}').replace('[镇民]','[townpeople]').replace('{/尺寸}','{/size}').replace('{size=*0。5}','{size=*0.5}').replace('[persistent。coins]','[persistent.coins]')
            if not allow_tag_repair or controls(repaired)!=controls(value):raise ValueError('Protected text changed: '+str(key))
        quote=row['quote']
        if re.search(r'(?<!\\)'+re.escape(quote),value):raise ValueError('Unescaped string quote: '+str(key))
        if '\n' in value or '\r' in value:raise ValueError('Literal newline not allowed')
        before[str(key)]=dict(original=old,target=value,file=row['file'],line=row['line'])
        row['target']=value;row['status']='reviewed';row['review']=name
    for key in review_ids or []:
        row=rows[int(key)]
        if row['status']=='pending':row['status']='reviewed';row['review']=name
    (ROOT/'review/batches').mkdir(parents=True,exist_ok=True)
    p=ROOT/'review/batches'/f'{name}.json'
    p.write_text(json.dumps(dict(name=name,changes=before,reviewed_ids=list(review_ids or [])),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,'changed',len(before),'reviewed',sum(r['status']=='reviewed' for r in rows),'total',len(rows))

if __name__=='__main__':
    p=ROOT/'review'/sys.argv[1];data=json.loads(p.read_text('utf-8'))
    apply(p.stem,data['changes'],data.get('review_ids'),data.get('allow_tag_repair',False))
