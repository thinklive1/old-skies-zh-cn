from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]

def read_json(p):
    def unique_object(pairs):
        obj={}
        for key,value in pairs:
            if key in obj:raise ValueError('Duplicate JSON key: '+key)
            obj[key]=value
        return obj
    return json.loads(Path(p).read_text(encoding='utf-8'),object_pairs_hook=unique_object)
def write_json(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def load(root=ROOT):
    original=read_json(root/'source/catalog.en.json'); translations={}; locations={}
    for p in sorted((root/'translation').glob('*.json')):
        for r in read_json(p):
            if r['id'] in translations: raise ValueError('Duplicate translation ID: '+r['id'])
            translations[r['id']]=r;locations[r['id']]=p
    if set(translations)!={r['id'] for r in original}: raise ValueError('Catalog/translation IDs mismatch')
    for r in original:
        t=translations[r['id']]
        if t['source']!=r['source'] or hashlib.sha256(r['source'].encode()).hexdigest()[:16]!=r['id']:
            raise ValueError('Changed source or ID: '+r['id'])
    return original,translations,locations

def protected(s):
    voice=re.match(r'^&\d+\s*',s)
    matches=re.finditer(r'%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?(?:[hlL]+)?[diuoxXfFeEgGaAcsp%]',s)
    # English prose such as "99% of it" is not printf's "% o".
    # Only exclude the unambiguous digit-percent-space case; keep legitimate
    # space-flag placeholders elsewhere and protect the percentage itself.
    printf=[m[0] for m in matches if not (m.start()>0 and s[m.start()-1].isdigit() and m[0].startswith('% '))]
    return dict(voice=voice[0] if voice else '',
      printf=printf,percentages=re.findall(r'\d+(?:\.\d+)?%(?![A-Za-z])',s),
      macros=re.findall(r'@[A-Za-z0-9_]+@',s),linebreaks=s.count('['),
      escapes=re.findall(r'\\[nrt\[\\]',s))

def errors(r):
    out=[]
    if r['status'] not in {'untranslated','translated','reviewed','excluded','preserve'}: out.append('invalid status')
    if r['status'] in {'translated','reviewed','preserve'}:
        if not r['target'].strip(): out.append('empty translation')
        if '\x00' in r['target'] or '\ufffd' in r['target']:out.append('invalid character')
        if protected(r['source'])!=protected(r['target']):out.append('changed protected tokens')
    if r['status']=='excluded' and not r['reason']:out.append('missing exclusion reason')
    return out
