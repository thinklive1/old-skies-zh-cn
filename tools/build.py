import argparse,collections,hashlib,json,shutil
from catalog import ROOT,read_json,write_json,load,errors
from tra import compile_tra,parse_tra
from record_review import receipt_hash
from encoding_bridge import select_pairs
from context_data import aliases

def build(development=False):
    cfg=read_json(ROOT/'project.json');baseline=read_json(ROOT/'source/baseline.json')
    if hashlib.sha256((ROOT/'source/catalog.en.json').read_bytes()).hexdigest()!=baseline['source_sha256']:raise ValueError('English catalog checksum mismatch')
    original,data,_=load();issues=[];pairs=[];counts=collections.Counter();receipts=set()
    for p in (ROOT/'review/receipts').glob('*.json'):
        receipts.update((r['id'],r['sha256']) for r in read_json(p)['entries'])
    for row in original:
        r=data[row['id']];counts[r['status']]+=1
        issues += [dict(id=r['id'],error=e) for e in errors(r)]
        if r['status']=='reviewed' and (r['id'],receipt_hash(r)) not in receipts:issues.append(dict(id=r['id'],error='review receipt missing or invalidated'))
    pairs,bridges=select_pairs([data[r['id']] for r in original],development)
    if issues:raise ValueError(json.dumps(issues,ensure_ascii=False))
    if not development and (counts['untranslated'] or counts['translated']):
        raise ValueError(f'Release blocked: {counts["untranslated"]} untranslated, {counts["translated"]} unreviewed')
    if not development:
        for path in (ROOT/'review/issues').glob('*.json'):
            issue=read_json(path)
            if issue.get('release_blocking') and issue.get('status')!='resolved':raise ValueError('Unresolved release issue: '+issue['id'])
        gates=read_json(ROOT/'review/release-gates.json')
        if not all(v is True for v in gates.values()) or cfg['release_state']!='ready':raise ValueError('Editorial/technical release gates not completed')
    game=read_json(ROOT/'source/game.json');tra=compile_tra(pairs,game['game_uid'],game['game_name'])
    parsed=parse_tra(tra)
    if parsed['pairs']!=dict(pairs) or parsed['uid']!=game['game_uid'] or parsed['name']!=game['game_name']:raise ValueError('TRA round-trip mismatch')
    dest=ROOT/'build'/('development' if development else 'release');dest.mkdir(parents=True,exist_ok=True)
    filename=cfg['translation_name']+'.tra';(dest/filename).write_bytes(tra)
    manifest=dict(project=cfg['name'],version=cfg['version'],development=development,
      complete=not(counts['untranslated'] or counts['translated']),counts=dict(counts),
      entries_in_tra=len(pairs),identity_encoding_bridges=len(bridges),identity_bridge_ids=bridges,game_uid=game['game_uid'],exe_sha256=baseline['exe_sha256'],
      context_data_required=True,context_aliases=[dict(id=uid,source=e['source'],runtime_key=e['runtime_key']) for uid,e in aliases().items()],
      files=[dict(name=filename,size=len(tra),sha256=hashlib.sha256(tra).hexdigest())])
    write_json(dest/'build-manifest.json',manifest);print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--development',action='store_true');build(ap.parse_args().development)
