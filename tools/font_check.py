from pathlib import Path
from catalog import ROOT
import io,pickle,zlib,struct,json,re,collections
class Safe(pickle.Unpickler):
    def find_class(self,m,n):raise ValueError('Unsafe RPA index')
def cmap(data):
    count=struct.unpack_from('>H',data,4)[0];offset=None
    for i in range(count):
        tag,checksum,start,size=struct.unpack_from('>4sIII',data,12+i*16)
        if tag==b'cmap':offset=start
    if offset is None:return set()
    result=set();n=struct.unpack_from('>H',data,offset+2)[0]
    for i in range(n):
        platform,encoding,relative=struct.unpack_from('>HHI',data,offset+4+i*8)
        if platform not in (0,3):continue
        at=offset+relative;fmt=struct.unpack_from('>H',data,at)[0]
        if fmt==12:
            groups=struct.unpack_from('>I',data,at+12)[0]
            for j in range(groups):
                first,last,glyph=struct.unpack_from('>III',data,at+16+j*12)
                for ch in range(first,min(last,0x10ffff)+1):
                    if glyph+ch-first:result.add(ch)
        elif fmt==4:
            segments=struct.unpack_from('>H',data,at+6)[0]//2
            ends=at+14;starts=ends+segments*2+2;deltas=starts+segments*2;ranges=deltas+segments*2
            for j in range(segments):
                first=struct.unpack_from('>H',data,starts+j*2)[0];last=struct.unpack_from('>H',data,ends+j*2)[0]
                delta=struct.unpack_from('>h',data,deltas+j*2)[0];rng=struct.unpack_from('>H',data,ranges+j*2)[0]
                for ch in range(first,last+1):
                    glyph=(ch+delta)&65535 if not rng else struct.unpack_from('>H',data,ranges+j*2+rng+(ch-first)*2)[0]
                    if rng and glyph:glyph=(glyph+delta)&65535
                    if glyph:result.add(ch)
    return result
fontsets={}
with Path(r'D:\software\steam\steamapps\common\oath\game\archive.rpa').open('rb') as f:
    h=f.readline().split();f.seek(int(h[1],16));index=Safe(io.BytesIO(zlib.decompress(f.read()))).load();key=int(h[2],16)
    for name in ['unif.otf','cc2.ttf','msi.ttf']:
        data=bytearray()
        for e in index[name]:
            f.seek(e[0]^key);data.extend(e[2] if len(e)>2 else b'');data.extend(f.read(e[1]^key))
        fontsets[name]=cmap(data)
rows=json.loads((ROOT/'catalog.json').read_text('utf-8'));missing=[]
for row in rows:
    if row['target']==row['original']:continue
    active='unif.otf';stack=[]
    for part in re.split(r'(\{[^}]*\}|\[[^\]]*\])',row['target']):
        m=re.fullmatch(r'\{font=(.+)\}',part)
        if m:stack.append(active);active=m[1];continue
        if part=='{/font}':active=stack.pop() if stack else 'unif.otf';continue
        if part.startswith(('{','[')):continue
        if active not in fontsets:continue
        absent={c for c in part if '\u3400'<=c<='\u9fff' and ord(c) not in fontsets[active]}
        if absent:missing.append(dict(id=row['id'],font=active,chars=''.join(sorted(absent))))
body_missing=[x for x in missing if x['font']!='cc2.ttf']
report=dict(fonts_unchanged=True,checked_fonts={k:len(v) for k,v in fontsets.items()},
    changed_text_entries_checked=sum(r['target']!=r['original'] for r in rows),
    main_chinese_font_missing=body_missing,legacy_special_font_findings=missing,
    special_font_note='Existing cc2.ttf has no Chinese glyphs. Its settings and file are preserved under the text-only scope. This report does not certify visible rendering of deliberately obscured/styled text.',
    main_font_success=not body_missing,special_font_rendering_verified=False)
(ROOT/'review/font-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='legacy_special_font_findings'},ensure_ascii=False,indent=2))
print('Legacy special-font findings:',len(missing))
raise SystemExit(0 if report['main_font_success'] else 1)
