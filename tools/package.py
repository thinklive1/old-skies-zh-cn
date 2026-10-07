"""Create a local, explicit-payload release candidate; never include game EXE.

The generated data/fonts are for this user's owned copy. Packaging is not an
authorization to publish original or derived game resources to a remote host.
"""
import hashlib, zipfile
from pathlib import Path
from catalog import ROOT, read_json, write_json
from install import digest


def package():
    cfg=read_json(ROOT/'project.json');manifest=read_json(ROOT/'build/release/build-manifest.json')
    if manifest['development'] or not manifest['complete'] or manifest['version']!=cfg['version'] or cfg['release_state']!='ready':
        raise ValueError('A current verified release build is required')
    files=[]
    for item in manifest['files']:
        p=ROOT/'build/release'/item['name']
        if digest(p)!=item['sha256']:raise ValueError('Stale payload '+item['name'])
        files.append(p)
    if len(files)!=10:raise ValueError('Unexpected payload count')
    files += [ROOT/'build/release/build-manifest.json',ROOT/'project.json',ROOT/'source/runtime-keys.json',
              ROOT/'tools/install.py',ROOT/'tools/catalog.py',ROOT/'README.md',ROOT/'CHANGELOG.md',ROOT/'review/acceptance.json']
    files += [p for p in (ROOT/'fonts').rglob('*') if p.is_file() and ('LICENSE' in p.name or p.name.startswith('OFL'))]
    dest=ROOT/'dist';dest.mkdir(exist_ok=True);output=dest/f'Technobabylon_zh_CN_{cfg["version"]}.zip'
    instructions='''Technobabylon 简体中文汉化 1.0.0-rc.1

全文与第二轮校对已完成，技术验证通过；游戏画面由用户验收。
仅适配 Steam build 24559207 / AGS 3.6.1.35 的已校验 EXE。

关闭游戏，解压本包后在解压目录执行（需 Python 3.10+）：
python tools/install.py install "D:\\software\\steam\\steamapps\\common\\Technobabylon"

安装器会自动备份、校验资源并选中中文。不要手动复制配置覆盖个人设置。
恢复原版：python tools/install.py rollback "<游戏目录>\\_Technobabylon_zh_CN_backup\\<备份编号>"

安装不修改原 EXE、语音、音乐或真实存档。
本包包含由用户本机原版生成的外置数据与派生字体；仅本机交付，未上传或公开发布。
'''
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in sorted(set(files)):
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),(2026,10,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,p.read_bytes())
        archive.writestr(zipfile.ZipInfo('安装说明.txt',(2026,10,7,0,0,0)),instructions.encode('utf-8'))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip():raise ValueError('ZIP CRC failed')
        for p in files:
            if hashlib.sha256(archive.read(p.relative_to(ROOT).as_posix())).hexdigest()!=digest(p):raise ValueError('ZIP payload mismatch')
    report=dict(version=cfg['version'],path=str(output),size=output.stat().st_size,sha256=digest(output),zip_crc_verified=True,
      payload_files=manifest['files'],published=False,visual_acceptance='pending-user')
    write_json(ROOT/'review/qa/package-check.json',report)
    print(f'Package verified: {output} ({report["size"]} bytes)')
    return output


if __name__=='__main__':package()
