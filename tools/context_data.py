"""Build bounded runtime localization fixes from a verified local asset."""
import argparse, hashlib
import struct
from pathlib import Path
from catalog import ROOT, read_json, write_json, protected
from scom_runtime import translate_scrollers


def recipe():
    return read_json(ROOT / 'source/runtime-keys.json')


def aliases():
    result = {}
    keys = set()
    for entry in recipe()['entries']:
        source, key = entry['source'], entry['runtime_key']
        if hashlib.sha256(source.encode('utf-8')).hexdigest()[:16] != entry['id']:
            raise ValueError('Runtime recipe source ID mismatch')
        if source == key or len(source.encode('cp1252')) != len(key.encode('cp1252')):
            raise ValueError('Runtime recipe must use a different same-length key')
        if protected(source) != protected(key) or key in keys or entry['id'] in result:
            raise ValueError('Unsafe or duplicate runtime alias')
        result[entry['id']] = entry
        keys.add(key)
    return result


def patch_asset(original, spec):
    if len(original) != spec['asset_size'] or hashlib.sha256(original).hexdigest() != spec['source_sha256']:
        raise ValueError('Unsupported source game data; refused to patch')
    modified = bytearray(original)
    for entry in spec['entries']:
        before = entry['source'].encode('cp1252')
        after = entry['runtime_key'].encode('cp1252')
        if len(before) != len(after):
            raise ValueError('Runtime alias changed string length')
        for offset in (entry['story_offset'], entry['commentary_offset']):
            if offset < 0 or original[offset:offset + len(before) + 1] != before + b'\0':
                raise ValueError('Story/commentary source bytes mismatch')
        offset = entry['story_offset']
        modified[offset:offset + len(before)] = after
    for control in spec.get('gui_controls', []):
        offset = control['offset']
        fingerprint = bytes.fromhex(control['fingerprint'])
        if offset < 0 or original[offset:offset+len(fingerprint)] != fingerprint:
            raise ValueError('GUI control fingerprint mismatch')
        before, after = control['before_flags'], control['after_flags']
        if before & 0x80 or after != before | 0x80:
            raise ValueError('GUI patch must only enable the translated flag')
        if original[offset:offset+4] != struct.pack('<i',before):
            raise ValueError('GUI control flags mismatch')
        modified[offset:offset+4] = struct.pack('<i',after)
    changes = [i for i, (a, b) in enumerate(zip(original, modified)) if a != b]
    if len(modified) != len(original) or changes != spec['changed_bytes']:
        raise ValueError('Unexpected game data changes')
    hook = spec.get('scroller_hook')
    if hook:
        if hashlib.sha256(modified).hexdigest() != spec['base_patched_sha256']:
            raise ValueError('Base GUI/context data checksum mismatch')
        start, size = hook['offset'], hook['source_size']
        blob = bytes(modified[start:start+size])
        if start < 0 or hashlib.sha256(blob).hexdigest() != hook['source_sha256']:
            raise ValueError('Scroller module checksum mismatch')
        patched, report = translate_scrollers(blob, read_json(ROOT/'source/scom-instructions.json'))
        if hashlib.sha256(patched).hexdigest() != hook['patched_sha256'] or report != hook['report']:
            raise ValueError('Scroller detour recipe mismatch')
        modified = modified[:start] + patched + modified[start+size:]
        if len(modified) != spec['patched_size']:
            raise ValueError('Patched runtime data size mismatch')
    if hashlib.sha256(modified).hexdigest() != spec['patched_sha256']:
        raise ValueError('Patched game data checksum mismatch')
    for entry in spec['entries']:
        before = entry['source'].encode('cp1252') + b'\0'
        offset = entry['commentary_offset']
        if modified[offset:offset + len(before)] != before:
            raise ValueError('Commentary bytes changed')
    return bytes(modified)


def build(assets, development=False):
    spec = recipe()
    aliases()  # Validate recipe IDs, voice markers and uniqueness too.
    dest = ROOT / 'build' / ('development' if development else 'release')
    path = dest / 'build-manifest.json'
    manifest = read_json(path)
    if manifest['development'] != development or not manifest.get('context_data_required'):
        raise ValueError('Build has not selected contextual runtime keys')
    data = patch_asset((Path(assets) / spec['asset_name']).read_bytes(), spec)
    filename = spec['asset_name']
    (dest / filename).write_bytes(data)
    manifest['files'] = [r for r in manifest['files'] if r['name'] != filename] + [
        dict(name=filename, size=len(data), sha256=hashlib.sha256(data).hexdigest())]
    manifest['context_data'] = dict(source_sha256=spec['source_sha256'],
        patched_sha256=spec['patched_sha256'], changed_bytes=spec['changed_bytes'],
        commentary_bytes_unchanged=True,
        gui_translation_controls=[c['name'] for c in spec.get('gui_controls',[])],
        prewrap_translation=bool(spec.get('scroller_hook')))
    write_json(path, manifest)
    write_json(dest / 'context-data-check.json', manifest['context_data'])
    print('Runtime data verified: story aliases, GUI draw flags and pre-wrap translation; commentary unchanged')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('assets')
    parser.add_argument('--development', action='store_true')
    args = parser.parse_args()
    build(args.assets, args.development)
