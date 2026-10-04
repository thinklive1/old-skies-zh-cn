"""Merge a reviewed section with locked original text; report every propagated edit."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PREFIX=re.compile(r'^&\d+\s*')
def body(s):return PREFIX.sub('',s).strip()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('edits');ap.add_argument('--start',type=int);ap.add_argument('--end',type=int);ap.add_argument('--propagate-identical',action='store_true');args=ap.parse_args()
    original=json.loads((ROOT/'source/original.v1.0.json').read_text(encoding='utf-8'))
    path=ROOT/'source/translations.v1.1.json';data=json.loads(path.read_text(encoding='utf-8'))
    edits=json.loads(Path(args.edits).read_text(encoding='utf-8'))
    policy_path=ROOT/'review/preserve_commentary.json'
    preserved=set(json.loads(policy_path.read_text(encoding='utf-8'))['ids']) if policy_path.exists() else set()
    for i in preserved:
        edits.pop(str(i),None)
    # Validate the entire batch before changing any entry; a mistyped ID must not
    # move a voiced line into a neighbouring entry.
    for key,text in edits.items():
        i=int(key)
        if not 0<=i<len(data):raise ValueError(i)
        before=PREFIX.match(original[i]['zh']);after=PREFIX.match(text)
        if (before.group(0).strip() if before else None)!=(after.group(0).strip() if after else None):
            raise ValueError(f'{i}: voice prefix differs from original')
    for key,text in edits.items():
        i=int(key)
        if not 0<=i<len(data):raise ValueError(i)
        if data[i]['id']!=i or data[i]['en']!=original[i]['en']:raise ValueError('identity mismatch')
        data[i]['zh']=text;data[i]['review_status']='reviewed'
    propagated=[]
    if args.propagate_identical:
        mapping={(body(original[int(i)]['en']),body(original[int(i)]['zh'])):body(text) for i,text in edits.items()}
        for a,b in zip(original,data):
            if b['id'] in preserved:continue
            key=(body(a['en']),body(a['zh']))
            if key not in mapping or b['zh']!=a['zh'] or body(b['zh'])==mapping[key]:continue
            # Both English and original Chinese must match. No matching by English alone.
            prefix=PREFIX.match(a['zh']);trailing=a['zh'][len(a['zh'].rstrip()):]
            b['zh']=(prefix.group(0) if prefix else '')+mapping[key]+trailing
            b['review_status']='needs_context_check'
            propagated.append(b['id'])
    if args.start is not None or args.end is not None:
        if args.start is None or args.end is None:raise ValueError('both bounds required')
        for b in data[args.start:args.end]:
            if b['review_status']!='needs_context_check':b['review_status']='reviewed'
    for i in preserved:
        data[i]['zh']=original[i]['zh']
        data[i]['scope']='preserve_upstream_commentary'
        data[i]['review_status']='reviewed'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'explicit_edits':len(edits),'propagated_need_context_check':propagated},ensure_ascii=False))
if __name__=='__main__':main()
