"""Apply explicit, human-audited scope decisions; never guess from text shape."""
import argparse
from catalog import ROOT, read_json, write_json, load, errors

def resolve(filename):
    batch=read_json(filename);_,rows,locations=load();touched=set();seen=set()
    for item in batch['entries']:
        uid=item['id']
        if uid in seen:raise ValueError('Duplicate scope decision')
        seen.add(uid);r=rows[uid]
        if r['source']!=item['source']:raise ValueError('Scope source mismatch: '+uid)
        if r['status'] in {'translated','reviewed'}:
            # An explicit audit may correct an identity entry's accounting only.
            # A changed translation can never be discarded through this path.
            if not (item.get('identity_only_rescope') is True and item['status']=='preserve' and r['target']==r['source']):
                raise ValueError('Refused to discard translated work: '+uid)
        if item['status'] not in {'preserve','excluded'} or not item['reason']:raise ValueError('Invalid scope decision')
        candidate={**r,'status':item['status'],'reason':item['reason'],
                   'target':r['source'] if item['status']=='preserve' else ''}
        if errors(candidate):raise ValueError(str(errors(candidate)))
        rows[uid]=candidate;touched.add(locations[uid])
    for p in touched:write_json(p,[rows[r['id']] for r in read_json(p)])
    print(f'Applied {len(seen)} explicit scope decisions')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('batch');resolve(ap.parse_args().batch)
