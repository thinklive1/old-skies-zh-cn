"""Update extraction context only; refuse any changed English key set."""
from collections import OrderedDict
from pathlib import Path
import argparse,hashlib
from catalog import ROOT,read_json,write_json

def refresh(raw):
    d=read_json(raw);grouped=OrderedDict()
    for occurrence in d['entries']:
        o=dict(occurrence);s=o.pop('source');grouped.setdefault(s,[]).append(o)
    path=ROOT/'source/catalog.en.json';catalog=read_json(path)
    if set(grouped)!={r['source'] for r in catalog}:raise ValueError('Source key set changed; explicit version migration needed')
    before=hashlib.sha256(path.read_bytes()).hexdigest()
    for r in catalog:r['occurrences']=grouped[r['source']]
    write_json(path,catalog);after=hashlib.sha256(path.read_bytes()).hexdigest()
    baseline=read_json(ROOT/'source/baseline.json');baseline['source_sha256']=after;write_json(ROOT/'source/baseline.json',baseline)
    write_json(ROOT/'review/context-migration.json',dict(before=before,after=after,reason='Map each SCOM reference to its actual source section using code offsets; English keys and translation IDs unchanged',entries=len(catalog)))
    print(f'Updated context for {len(catalog)} unchanged source keys')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('raw');refresh(ap.parse_args().raw)
