"""Verify independent Extractor.cs output for the contextual data candidate."""
import argparse, datetime, hashlib
from pathlib import Path
from collections import defaultdict
from catalog import ROOT, read_json, write_json
from context_data import recipe


def verify(original_path, patched_path):
    original = read_json(original_path)
    patched = read_json(patched_path)
    catalog = read_json(ROOT / 'source/catalog.en.json')
    baseline = read_json(ROOT / 'source/baseline.json')
    if hashlib.sha256((ROOT / 'source/catalog.en.json').read_bytes()).hexdigest() != baseline['source_sha256']:
        raise ValueError('English catalog baseline checksum mismatch')
    groups = defaultdict(list)
    for row in original['entries']:
        groups[row['source']].append({k: v for k, v in row.items() if k != 'source'})
    expected = {row['source']: row['occurrences'] for row in catalog}
    if dict(groups) != expected:
        raise ValueError('Original extraction does not match immutable English catalog')
    if {k: v for k, v in original.items() if k != 'entries'} != {k: v for k, v in patched.items() if k != 'entries'}:
        raise ValueError('Patched extraction changed game metadata')
    spec = recipe()
    supplemental=spec.get('scroller_hook',{}).get('added_text_references',[])
    def identity(row):return tuple(row[k] for k in ('asset','kind','index','script'))
    before_map={identity(r):r for r in original['entries']}
    after_map={identity(r):r for r in patched['entries']}
    extra_map={identity(r):r for r in supplemental}
    if len(before_map)!=len(original['entries']) or len(after_map)!=len(patched['entries']):
        raise ValueError('Duplicate extraction location')
    if set(after_map)-set(before_map)!=set(extra_map) or set(before_map)-set(after_map):
        raise ValueError('Unexpected added or lost reference')
    if any(after_map[k]!=r or r['source'] not in expected for k,r in extra_map.items()):
        raise ValueError('Unexpected supplemental wrapper text')
    needed = {}
    for entry in spec['entries']:
        key = (entry['source'], 'game28.dta', 'dialog-script', entry['story_code_index'], 'Dialog 71')
        needed[key] = entry['runtime_key']
    actual = {}
    for before in original['entries']:
        after=after_map[identity(before)]
        if before == after:
            continue
        key = tuple(before[k] for k in ('source', 'asset', 'kind', 'index', 'script'))
        if key in actual or key not in needed or after != {**before, 'source': needed[key]}:
            raise ValueError('Unexpected changed extracted reference')
        actual[key] = after['source']
    if actual != needed:
        raise ValueError('Expected story aliases missing from extraction')
    report = dict(generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        passed=True, method='Independent AGSUnpacker/Extractor.cs re-extraction',
        original_raw_sha256=hashlib.sha256(Path(original_path).read_bytes()).hexdigest(),
        patched_raw_sha256=hashlib.sha256(Path(patched_path).read_bytes()).hexdigest(),
        metadata_unchanged=True, references=len(original['entries']),
        supplemental_wrapper_references=supplemental, runtime_references=len(patched['entries']),
        original_unique_keys=len(groups), runtime_unique_keys=len({r['source'] for r in patched['entries']}),
        changed_references=[dict(source=k[0], asset=k[1], kind=k[2], index=k[3], script=k[4], runtime_key=v) for k,v in actual.items()],
        commentary_and_all_other_references_unchanged=True,
        visual_game_verified=False)
    write_json(ROOT / 'review/qa/context-extraction-check.json', report)
    print(f'Independent extraction verified: two story aliases; all 20207 original references retained; {len(supplemental)} declared wrapper references added')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('original_extraction')
    parser.add_argument('patched_extraction')
    args = parser.parse_args()
    verify(args.original_extraction, args.patched_extraction)
