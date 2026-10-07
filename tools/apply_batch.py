"""Apply an explicit source/target mapping; no translation generation or fuzzy match."""
import argparse
from catalog import ROOT,load,write_json,errors,read_json

def apply(batch):
    mapping=read_json(batch);_,data,locations=load();sources={r['source']:r for r in data.values()}
    if isinstance(mapping,dict):mapping=[{'id':uid,'target':target} for uid,target in mapping.items()]
    if not isinstance(mapping,list):raise ValueError('Batch must be a list or exact ID map')
    touched=set();seen=set()
    for item in mapping:
        source=item['source'] if 'source' in item else data[item['id']]['source']
        target=item['target']
        if source in seen:raise ValueError('Repeated batch source: '+source)
        seen.add(source)
        if source not in sources:raise ValueError('Unknown source: '+repr(source))
        r=sources[source]
        if r['status']=='excluded':raise ValueError('Excluded item: '+source)
        candidate={**r,'target':target,'status':'translated','review_notes':item.get('notes','')}
        e=errors(candidate)
        if e:raise ValueError(repr(source)+': '+str(e))
        data[r['id']]=candidate;touched.add(locations[r['id']])
    # All input validation finishes before the first write.
    for p in touched:
        rows=read_json(p);write_json(p,[data[r['id']] for r in rows])
    print(f'Applied {len(mapping)} explicit translations to {len(touched)} shards')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('batch');apply(ap.parse_args().batch)
