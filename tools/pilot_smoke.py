"""Install, run and roll back a marked private copy using SDL dummy backends.

Does not exercise gameplay, visible layout or Steam integration. Language is
selected by installed acsetup.cfg, not a command-line translation override.
"""
import argparse, contextlib, datetime, io, os, subprocess, time, uuid
from pathlib import Path
from catalog import ROOT, read_json, write_json
from install import install, rollback, digest

def smoke(game, release=False):
    game=Path(game).resolve();marker=read_json(game/'.technobabylon-test-copy.json')
    if marker.get('isolated_copy') is not True or marker.get('exe_sha256')!=digest(game/'Technobabylon.exe'):
        raise ValueError('Missing or invalid private-copy marker; refused to install/run')
    manifest=read_json(ROOT/'build'/('release' if release else 'development')/'build-manifest.json')
    names=[r['name'] for r in manifest['files']]+['acsetup.cfg']
    before={n:digest(game/n) for n in names}
    run_dir=game/('test-run-'+uuid.uuid4().hex[:8]);run_dir.mkdir()
    for d in ['userdata','shared','logs']:(run_dir/d).mkdir()
    args=[str(game/'Technobabylon.exe'),'--localuserconf','--windowed','--gfxdriver','Software',
          '--gfxfilter','StdScale','1','--no-message-box','--log-file=all:debug',
          '--log-file-path='+str(run_dir/'logs'),'--user-data-dir',str(run_dir/'userdata'),
          '--shared-data-dir',str(run_dir/'shared')]
    record=dict(generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                version=manifest['version'],isolated_copy=True,engine='3.6.1.35',
                build_files=manifest['files'],args=args,
                language_selection='installed acsetup.cfg; no --translation override',
                visual_game_verified=False,steam_integration='not verified',passed=False)
    backup=None;process=None;log=''
    try:
        with contextlib.redirect_stdout(io.StringIO()) as cap:backup=install(game,not release)
        if manifest.get('context_data_required'):
            context_hash=digest(game/'game28.dta')
            if context_hash!=manifest['context_data']['patched_sha256']:
                raise ValueError('Installed contextual data hash mismatch')
            record['context_data_sha256']=context_hash
            record['contextual_dialogue_visual_test']='not exercised; startup room only'
        (ROOT/'review/qa/pilot-install-log.txt').write_text(cap.getvalue(),encoding='utf-8')
        env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'}
        startup=None
        if os.name=='nt':
            startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        begin=time.monotonic()
        with (run_dir/'stdout.txt').open('wb') as out,(run_dir/'stderr.txt').open('wb') as err:
            process=subprocess.Popen(args,cwd=game,env=env,stdout=out,stderr=err,startupinfo=startup)
            alive=False
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                alive=True;process.terminate();process.wait(timeout=10)
        record.update(duration_seconds=round(time.monotonic()-begin,2),remained_running_during_observation=alive,
                      ended='owned test process stopped after observation' if alive else 'process exited before observation finished')
        log=(run_dir/'logs/ags.log').read_text('utf-8',errors='replace')
        checks={'translation_loaded':'Translation loaded: Technobabylon_zh_CN.tra' in log,
                'utf8_initialized':'Translation initialized: Technobabylon_zh_CN (format: UTF-8)' in log,
                'engine_started':'Engine initialization complete' in log,
                'startup_room_entered':'Now in room 2' in log,
                'all_fonts_loaded':all(f'Loaded font {i}: agsfnt{i}.ttf' in log for i in range(8)),
                'process_survived':alive}
        record['checks']=checks;record['passed']=all(checks.values())
    except Exception as error:
        record['error']=str(error)
    finally:
        if process is not None and process.poll() is None:process.terminate();process.wait(timeout=10)
        if backup:
            try:
                with contextlib.redirect_stdout(io.StringIO()):rollback(backup)
                restored={n:digest(game/n) for n in names}
                record['rollback_byte_exact']=before==restored
                write_json(ROOT/'review/qa/pilot-install-rollback.json',dict(build_files=manifest['files'],before=before,restored=restored,byte_exact_restore=before==restored,backup=str(backup),isolated_copy=True))
            except Exception as error:record['rollback_error']=str(error);record['rollback_byte_exact']=False
        else:record['rollback_byte_exact']=False
        record['passed']=record['passed'] and record['rollback_byte_exact']
        (ROOT/'review/qa/engine-latest-full.log').write_text(log,encoding='utf-8')
        write_json(ROOT/'review/qa/engine-smoke.json',record)
    print('Engine load/config activation/rollback: '+('passed' if record['passed'] else 'FAILED'))
    return record['passed']

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('game_copy');ap.add_argument('--release',action='store_true');a=ap.parse_args()
    raise SystemExit(0 if smoke(a.game_copy,a.release) else 1)
