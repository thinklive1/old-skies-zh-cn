"""Record a completed editorial pass for explicitly selected batch entries.

Run only after reading the English and Chinese in context; this does not review
or generate translations automatically. A changed target invalidates the receipt.
"""
import argparse,hashlib,datetime
from catalog import ROOT,read_json,write_json,load,errors

def receipt_hash(r):return hashlib.sha256((r['source']+'\0'+r['target']).encode('utf-8')).hexdigest()
def record(batches,notes):
    original,rows,locations=load();by_source={r['source']:r['id'] for r in original};chosen=set()
    for filename in batches:
        batch=read_json(filename)
        chosen.update(batch if isinstance(batch,dict) else (item.get('id') or by_source[item['source']] for item in batch))
    touched=set();reviewed=[]
    for uid in sorted(chosen):
        r=rows[uid]
        if r['status'] not in {'translated','reviewed'}:raise ValueError('Not a translation: '+uid)
        if errors(r):raise ValueError('QA failed for '+uid)
        if r['review_notes']:continue # unresolved translator/context notes stay pending
        r['status']='reviewed';touched.add(locations[uid]);reviewed.append(dict(id=uid,sha256=receipt_hash(r)))
    name=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    write_json(ROOT/'review/receipts'/f'{name}.json',dict(reviewer='Codex',pass_type='second editorial pass',notes=notes,source_batches=[str(__import__('pathlib').Path(p).name) for p in batches],entries=reviewed))
    for p in touched:write_json(p,[rows[r['id']] for r in read_json(p)])
    print(f'Recorded {len(reviewed)} reviews; entries with unresolved notes remain translated')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('batches',nargs='+');ap.add_argument('--notes',required=True);a=ap.parse_args();record(a.batches,a.notes)
