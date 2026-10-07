"""Run catalog/format/installer checks, then build the selected candidate.

This is local validation. A development success does not mean a completed
translation, verified game layout, or permission to release/install publicly.
"""
import argparse, datetime, hashlib, os, subprocess, sys
from pathlib import Path
from catalog import ROOT, read_json, write_json

def check(assets=None, release=False):
    env={**os.environ,'PYTHONIOENCODING':'utf-8'}
    mode=[] if release else ['--development']
    commands=[['test_formats.py'],['test_context_data.py'],['test_scom_runtime.py'],['test_install.py'],['build.py',*mode]]
    if assets:
        absolute=str(Path(assets).resolve())
        commands += [['context_data.py',absolute,*mode],['build_fonts.py',absolute,*mode],['font_check.py',absolute,*mode]]
    commands.append(['progress.py'])
    results=[]
    for command in commands:
        run=subprocess.run([sys.executable,str(ROOT/'tools'/command[0]),*command[1:]],env=env,
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8')
        results.append(dict(tool=command[0],exit_code=run.returncode,output=run.stdout))
        print(command[0]+': '+('passed' if run.returncode==0 else 'FAILED'))
        if run.returncode:
            print(run.stdout);break
    manifest=ROOT/'build'/('release' if release else 'development')/'build-manifest.json'
    result=dict(generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                success=all(r['exit_code']==0 for r in results) and len(results)==len(commands),
                development=not release, fonts_included=bool(assets),
                build_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.exists() else None,
                results=results, visual_game_test='pending',
                complete_translation=read_json(manifest)['complete'] if manifest.exists() else False)
    write_json(ROOT/'review/qa/local-checks.json',result)
    return result['success']

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--assets');ap.add_argument('--release',action='store_true');a=ap.parse_args()
    raise SystemExit(0 if check(a.assets,a.release) else 1)
