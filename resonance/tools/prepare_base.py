"""Import the original v1.0.1 patch after checking its locked file hashes."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, shutil, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--original-zip', type=Path)
    group.add_argument('--original-dir', type=Path)
    args = parser.parse_args()
    lock = json.loads((ROOT/'baseline/source_lock.json').read_text(encoding='utf-8-sig'))
    destination = ROOT/'baseline/v1.0.1'
    if destination.exists():
        raise SystemExit('baseline/v1.0.1 already exists; keep it intact or choose a fresh checkout.')
    with tempfile.TemporaryDirectory(prefix='resonance-baseline-') as temp:
        staging = Path(temp)
        if args.original_zip:
            with zipfile.ZipFile(args.original_zip) as z:
                for info in z.infolist():
                    name = PurePosixPath(info.filename.replace('\\','/'))
                    if name.is_absolute() or '..' in name.parts or any(':' in p for p in name.parts):
                        raise SystemExit('Unsafe ZIP member: '+info.filename)
                z.extractall(staging)
            candidates = [p.parent for p in staging.rglob('patch_manifest.json')]
        else:
            candidates = [args.original_dir]
        selected = None
        for candidate in candidates:
            try:
                for item in lock['files']:
                    path = PurePosixPath(item['path'])
                    if path.is_absolute() or '..' in path.parts or any(':' in p for p in path.parts):
                        raise ValueError('Unsafe lock path')
                    data = (candidate/item['path']).read_bytes()
                    if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
                        raise ValueError('Baseline hash mismatch: '+item['path'])
                selected = candidate
                break
            except (OSError, ValueError):
                continue
        if selected is None:
            raise SystemExit('No original v1.0.1 patch matches all locked file hashes.')
        destination.mkdir(parents=True)
        for item in lock['files']:
            target = destination/item['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(selected/item['path'], target)
    print('Imported and verified',len(lock['files']),'original v1.0.1 files.')

if __name__ == '__main__':
    main()
