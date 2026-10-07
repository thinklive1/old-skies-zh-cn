import hashlib,io,json,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import install

class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.game=self.root/'game';self.game.mkdir()
        self.project=self.root/'project';self.build=self.project/'build/development';self.build.mkdir(parents=True)
        (self.game/'Technobabylon.exe').write_bytes(b'fake fixture exe')
        self.original=b'[graphics]\r\nwindowed=1\r\n[language]\r\ntranslation=\r\n[sound]\r\nusespeech=1\r\n'
        (self.game/'acsetup.cfg').write_bytes(self.original)
        (self.game/'agsfnt0.ttf').write_bytes(b'original-font')
        rows=[]
        for name in ['Technobabylon_zh_CN.tra']+[f'agsfnt{i}.ttf' for i in range(8)]:
            p=self.build/name;p.write_bytes(('new-'+name).encode());rows.append(dict(name=name,size=p.stat().st_size,sha256=install.digest(p)))
        (self.project/'project.json').write_text(json.dumps(dict(translation_name='Technobabylon_zh_CN')))
        manifest=dict(development=True,complete=False,version='test',exe_sha256=install.digest(self.game/'Technobabylon.exe'),files=rows)
        (self.build/'build-manifest.json').write_text(json.dumps(manifest))
        self.patcher=patch.object(install,'ROOT',self.project);self.patcher.start()
    def tearDown(self):self.patcher.stop();self.temp.cleanup()
    def call_install(self,**kwargs):
        with redirect_stdout(io.StringIO()):return install.install(self.game,True,**kwargs)
    def test_dry_run_never_writes(self):
        before={p.name:p.read_bytes() for p in self.game.iterdir()};self.call_install(dry_run=True)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.game.iterdir()})
    def test_install_and_repeatable_byte_exact_rollback(self):
        backup=self.call_install();self.assertEqual(install.digest(self.game/'agsfnt0.ttf'),install.digest(self.build/'agsfnt0.ttf'))
        with redirect_stdout(io.StringIO()):install.rollback(backup);install.rollback(backup)
        self.assertEqual((self.game/'acsetup.cfg').read_bytes(),self.original)
        self.assertEqual((self.game/'agsfnt0.ttf').read_bytes(),b'original-font')
        self.assertFalse((self.game/'agsfnt3.ttf').exists())
        self.assertFalse((self.game/'Technobabylon_zh_CN.tra').exists())
    def test_failure_midway_restores_original_files(self):
        original_copy=install.shutil.copyfile
        def fail_one(source,target,*args,**kwargs):
            if Path(target).name=='agsfnt2.ttf.technobabylon-tmp':raise OSError('injected staging failure')
            return original_copy(source,target,*args,**kwargs)
        with patch.object(install.shutil,'copyfile',side_effect=fail_one):
            with self.assertRaises(OSError):self.call_install()
        self.assertEqual((self.game/'acsetup.cfg').read_bytes(),self.original)
        self.assertEqual((self.game/'agsfnt0.ttf').read_bytes(),b'original-font')
        self.assertFalse((self.game/'agsfnt1.ttf').exists())
        self.assertFalse((self.game/'Technobabylon_zh_CN.tra').exists())
        self.assertFalse(list(self.game.glob('*.technobabylon-tmp')))
        receipt=next((self.game/'_Technobabylon_zh_CN_backup').glob('*/backup-manifest.json'))
        self.assertEqual(json.loads(receipt.read_text('utf-8'))['state'],'failed-restored')
    def test_modified_game_exe_is_refused_before_writes(self):
        (self.game/'Technobabylon.exe').write_bytes(b'wrong-version')
        with self.assertRaises(ValueError):self.call_install()
        self.assertEqual((self.game/'acsetup.cfg').read_bytes(),self.original)
        self.assertFalse((self.game/'_Technobabylon_zh_CN_backup').exists())
    def test_user_changed_installed_file_blocks_rollback(self):
        backup=self.call_install();(self.game/'agsfnt0.ttf').write_bytes(b'user-font')
        with self.assertRaises(ValueError):install.rollback(backup)
        self.assertEqual((self.game/'agsfnt0.ttf').read_bytes(),b'user-font')
        self.assertTrue((self.game/'agsfnt3.ttf').exists())
    def test_corrupted_backup_blocks_all_rollback_writes(self):
        backup=self.call_install();(backup/'acsetup.cfg').write_bytes(b'corrupted')
        with self.assertRaises(ValueError):install.rollback(backup)
        self.assertTrue((self.game/'Technobabylon_zh_CN.tra').exists())
    def test_relative_backup_path_injection_is_refused(self):
        backup=self.call_install();p=backup/'backup-manifest.json';j=json.loads(p.read_text('utf-8'))
        j['files'][0]['name']='../unsafe';p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):install.rollback(backup)
    def test_config_only_changes_language(self):
        patched=install.language_config(self.original,'Technobabylon_zh_CN')
        self.assertEqual(patched,self.original.replace(b'translation=\r\n',b'translation=Technobabylon_zh_CN\r\n'))
    def test_duplicate_config_refused(self):
        with self.assertRaises(ValueError):install.language_config(b'[language]\ntranslation=x\ntranslation=y\n','test')

    def context_build(self):
        original=b'original fixture game data';patched=b'patched fixture game data'
        source=self.project/'source';source.mkdir(exist_ok=True)
        spec=dict(asset_name='game28.dta',source_sha256=hashlib.sha256(original).hexdigest(),patched_sha256=hashlib.sha256(patched).hexdigest())
        (source/'runtime-keys.json').write_text(json.dumps(spec))
        path=self.build/'game28.dta';path.write_bytes(patched)
        manifest_path=self.build/'build-manifest.json';manifest=json.loads(manifest_path.read_text())
        manifest.update(context_data_required=True,context_data=spec)
        manifest['files'].append(dict(name=path.name,size=len(patched),sha256=install.digest(path)))
        manifest_path.write_text(json.dumps(manifest))
        return original,patched

    def test_context_data_install_restores_absence_and_existing_original(self):
        original,patched=self.context_build()
        for prior in (None,original):
            with self.subTest(existing=prior is not None):
                if prior is not None:(self.game/'game28.dta').write_bytes(prior)
                backup=self.call_install()
                self.assertEqual((self.game/'game28.dta').read_bytes(),patched)
                with redirect_stdout(io.StringIO()):install.rollback(backup);install.rollback(backup)
                self.assertEqual((self.game/'game28.dta').read_bytes() if (self.game/'game28.dta').exists() else None,prior)

    def test_unknown_external_context_data_refused(self):
        self.context_build();(self.game/'game28.dta').write_bytes(b'user-modified')
        with self.assertRaises(ValueError):self.call_install()
        self.assertEqual((self.game/'game28.dta').read_bytes(),b'user-modified')
        self.assertFalse((self.game/'_Technobabylon_zh_CN_backup').exists())

    def test_required_context_payload_missing_is_refused(self):
        self.context_build();path=self.build/'build-manifest.json';manifest=json.loads(path.read_text())
        manifest['files']=[r for r in manifest['files'] if r['name']!='game28.dta'];path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):self.call_install()
        self.assertFalse((self.game/'_Technobabylon_zh_CN_backup').exists())

    def test_modified_context_payload_blocks_rollback(self):
        self.context_build();backup=self.call_install();(self.game/'game28.dta').write_bytes(b'user-data')
        with self.assertRaises(ValueError):install.rollback(backup)
        self.assertTrue((self.game/'Technobabylon_zh_CN.tra').exists())

if __name__=='__main__':unittest.main()
