from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
QUOTED=re.compile(r'"(?:\\.|[^"\\\r\n])*"|\'(?:\\.|[^\'\\\r\n])*\'')
HAN=re.compile('[\u3400-\u9fff]')

def source_text(path):
    return path.read_bytes().decode('utf-8-sig').replace('\r\r\n','\n').replace('\r\n','\n')

def extract():
    originals={};rows=[]
    for p in sorted((ROOT/'source/tl/chinese').rglob('*.rpy')):
        where=None
        for line in source_text(p).splitlines():
            m=re.match(r'\s*# game/(.+?):(\d+)',line)
            if m:where=(m[1],int(m[2]));continue
            if where and line.lstrip().startswith('# '):
                strings=QUOTED.findall(line)
                if strings:originals[where]=strings[0][1:-1]
            elif where and line.lstrip().startswith('old '):
                strings=QUOTED.findall(line)
                if strings:originals[where]=strings[0][1:-1]
    for p in sorted((ROOT/'source').rglob('*.rpy')):
        rel=p.relative_to(ROOT/'source').as_posix();tl=rel.startswith('tl/')
        raw=p.read_bytes().decode('utf-8');label='';offset=0;old=None
        unusual_cr='\r\r\n' in raw
        # split only on LF, so source line numbering and original CRCRLF bytes are preserved.
        for number,line in enumerate(raw.splitlines(keepends=True) if not unusual_cr else raw.split('\n'),1):
            if unusual_cr:line+='\n' if offset+len(line)<len(raw) else ''
            strip=line.strip('\ufeff \r\n\t')
            m=re.match(r'label\s+([^:]+):',strip)
            if m:label=m[1]
            if strip.startswith('old '):
                matches=QUOTED.findall(line);old=matches[0][1:-1] if matches else None
            if strip.startswith('#') or not HAN.search(line):offset+=len(line);continue
            matches=list(QUOTED.finditer(line))
            for nth,m in enumerate(matches):
                value=m[0][1:-1]
                if not HAN.search(value):continue
                prefix=line[:m.start()].strip('\ufeff \t')
                display=(bool(re.match(r'^\w+\s*$',prefix)) and not prefix.startswith(('label','jump','call','scene','show','hide','play','queue','image','define','default','if','elif','while','return')))
                display=display or prefix=='' or '_(' in prefix or 'renpy.input(' in prefix
                display=display or prefix.startswith(('text ','textbutton ','tooltip ','label _('))
                if tl:display=strip.startswith('new ')
                if not display:continue
                rows.append(dict(id=len(rows),file=rel,line=number,occurrence=nth,label=label,
                    start=offset+m.start()+1,end=offset+m.end()-1,quote=m[0][0],original=value,
                    english=(old if tl else originals.get((rel,number))),target=value,status='pending'))
            offset+=len(line)
    (ROOT/'catalog.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Text entries:',len(rows),'English aligned:',sum(bool(r['english']) for r in rows))
    return rows

if __name__=='__main__':extract()
