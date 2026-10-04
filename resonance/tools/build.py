"""Reproducible v1.1 candidate build with structural validation and review report."""
from pathlib import Path
import json,hashlib,shutil,re,zipfile,html,collections
from tra_codec import extract,compile_tra
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'baseline/v1.0.1'
NAME='Resonance_简体中文汉化_v1.1_全量校对候选版'
PKG=ROOT/'build'/NAME
def sha(data):return hashlib.sha256(data).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 lock=json.loads((ROOT/'baseline/source_lock.json').read_text(encoding='utf-8'))
 for item in lock['files']:
  data=(BASE/item['path']).read_bytes()
  assert len(data)==item['bytes'] and sha(data)==item['sha256'],item['path']
 blob=(BASE/'PatchFiles/Chinese.tra').read_bytes();original,a,b=extract(blob)
 assert compile_tra(blob,original)==blob
 master=json.loads((ROOT/'source/translations.v1.1.json').read_text(encoding='utf-8'))
 changes=json.loads((ROOT/'source/change_log.json').read_text(encoding='utf-8'))
 assert len(master)==len(original)==10202
 assert len({r['id'] for r in changes})==len(changes)
 placeholders=re.compile(r'%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[sdifuxXc%]')
 markers=re.compile(r'^(?:<[2bilr])+')
 for old,new in zip(original,master):
  assert old['id']==new['id'] and old['en']==new['en'] and old['zh']==new['original_zh']
  assert '\0' not in new['zh'] and '\ufffd' not in new['zh']
  if old['zh']!=new['zh']:
   assert placeholders.findall(old['zh'])==placeholders.findall(new['zh']),('placeholder',new['id'])
   assert old['zh'].count('[')==new['zh'].count('['),('linebreak',new['id'])
   assert markers.findall(old['zh'])==markers.findall(new['zh']),('marker',new['id'])
 rebuilt=compile_tra(blob,master);decoded,a2,b2=extract(rebuilt)
 assert [(r['en'],r['zh']) for r in decoded]==[(r['en'],r['zh']) for r in master]
 assert blob[:a]==rebuilt[:a2] and blob[b:]==rebuilt[b2:]
 # Font coverage check; AGS rendering itself remains a separate playtest gate.
 from font_check import supported_codepoints
 changedchars={ord(c) for r in master for c in r['zh'] if ord(c)>127}
 font_root=ROOT/'source/fonts'
 font_checks=[]
 for font in sorted(font_root.glob('*.ttf')):
  missing=sorted(changedchars-supported_codepoints(font,changedchars))
  assert not missing,(font.name,''.join(map(chr,missing)))
  font_checks.append({'font':font.name,'all_non_ascii_codepoints':len(changedchars),'missing':missing})
 assert len(font_checks)==10
 shutil.copytree(BASE,PKG,dirs_exist_ok=True)
 (PKG/'PatchFiles/Chinese.tra').write_bytes(rebuilt)
 for font in font_root.glob('*.ttf'):shutil.copy2(font,PKG/'PatchFiles'/font.name)
 shutil.copy2(ROOT/'docs/字体补字说明.txt',PKG/'字体补字说明.txt')
 shutil.copy2(ROOT/'docs/OFL-v1.1新增字形.txt',PKG/'PatchFiles/OFL-v1.1新增字形.txt')
 script=(BASE/'安装汉化.ps1').read_text(encoding='utf-8-sig')
 assert "-ne '1.0.1'" in script
 script=script.replace("-ne '1.0.1'","-ne '1.1'").replace('版本 v1.0.1 正式版。','版本 v1.1 全量校对候选版（待游戏内验收）。')
 (PKG/'安装汉化.ps1').write_text(script,encoding='utf-8-sig')
 manifest=json.loads((BASE/'patch_manifest.json').read_text(encoding='utf-8'))
 manifest['version']='1.1'
 manifest['files'].append({'name':'OFL-v1.1新增字形.txt','path':'PatchFiles/OFL-v1.1新增字形.txt'})
 for item in manifest['files']:
  data=(PKG/item['path']).read_bytes();item['bytes']=len(data);item['sha256']=sha(data)
 dump(PKG/'patch_manifest.json',manifest)
 counts=dict(collections.Counter(r['status'] for r in master))
 verification={'version':'1.1','release_status':'candidate','date':'2026-10-03','baseline_version':'1.0.1','dictionary_pairs':len(master),'changed_pairs':len(changes),'review_status_counts':counts,'source_integrity':'passed','baseline_tra_byte_identical_roundtrip':'passed','english_keys_order_and_count':'passed','non_dictionary_blocks_unchanged':'passed','edited_placeholders_linebreaks_display_markers':'passed','compiled_tra_readback':'passed','font_coverage':font_checks,'journal_sync':json.loads((ROOT/'qa/journal_sync.json').read_text(encoding='utf-8')),'runtime_playtest':'not_run: game installed; display and story playtest pending','unreviewed_pairs':counts.get('inherited_not_reviewed',0),'scope':'全部10,202个TRA键完成校对；其中366个金额键逐项等值核验，其他9,836个键按9,506组双语审校；补齐同源字形；25条SRT完成中文通读，英文音轨与图像硬字幕、游戏内语境待验收。'}
 dump(ROOT/'qa/text_validation.json',verification);dump(PKG/'离线验证.json',verification)
 installer_report=ROOT/'qa/installer_tests.json'
 if installer_report.exists():
  installer=json.loads(installer_report.read_text(encoding='utf-8-sig'))
  assert installer['version']=='1.1' and installer['fixture_only'] is True and all(t['passed'] is True for t in installer['tests'])
  dump(PKG/'安装回退验证.json',installer)
 install=f'''Resonance 简体中文汉化 v1.1 全量校对候选版
简体中文汉化：B站up主 那卡nakami（沿用原包署名）

本包是 v1.0.1 的文本润色分支。已修订 {len(changes)} 对显示键（含同句变体与日记分行）。
全部10,202个翻译键已完成本轮校对。游戏内显示与剧情通关验收待完成，当前保留为候选版。

安装
1. 退出游戏，完整解压，不要直接在压缩软件内运行。
2. 如果已经安装旧汉化，请先用对应旧包的“回退汉化.bat”或卸载入口恢复原版。
   v1.0.1 必须用 v1.0.1 包回退；v1.1 只负责自身安装产生的备份。
3. 双击本包“安装汉化.bat”，选择含 Resonance.exe 的游戏目录。
4. 安装后确认对白、日记、手机、邮件和教程显示；异常时退出游戏后回退。

安装器核验包内清单和文件哈希，备份本次实际原件及配置。
保留游戏目录里的“_Resonance_简中备份”，安装需约 1.5GB 额外空间。
图片沿用 v1.0.1 的内容匹配机制；找不到对应图片时保留原图。
安装成功不代表已经完成游戏内显示与通关验收。

回退
退出游戏，运行本包“回退汉化.bat”，选择原游戏目录。
回退恢复安装前文件和配置；改动过的受管文件会先保存到独立的回退前备份目录。
不要用新包直接覆盖旧包的首次备份；不要删除原始备份。
安装、回退均不读写个人存档。

范围
英文翻译键、格式占位符、显示标记、换行标记与日记日期、分页保留。
解谜用的姓名、用户名、密码、坐标、密文及数字不得按文风改写。
本轮修订TRA译文、补入同源像素字形；图像、视频、游戏脚本与房间沿用原包。
外置SRT共25条字幕已通读中文，保留原译和时间轴；英文音轨与硬字幕尚待游戏内验收。
已知版本信息：原包记载 Steam App212050/build24412244、AGS3.6.1.35 已通关。
此为 v1.0.1 历史记录，不是 v1.1 通关记录。
本包不含完整游戏、私人存档或登录凭据。
'''
 (PKG/'安装说明.txt').write_text(install,encoding='utf-8-sig')
 release=f'''# Resonance 简体中文汉化 v1.1 全量校对候选版

本版以 v1.0.1 为基线，按自然口语、悬疑氛围与角色差异润色。
保留原包“简体中文汉化：B站up主 那卡nakami”及原作者、发行方署名。

## 文本改动

- 共修订 {len(changes)} 对显示键，包含 {counts.get('edited_direct',0)} 条直接审定、{counts.get('edited_same_english_variant',0)} 条同英文显示变体和 {counts.get('edited_journal_line',0)} 条日记行键。
- 修正“脚踝全搞砸了”“办公室彩票池”“法律用纸”、父亲误译为母亲等问题。
- 调整对白、物品说明、邮件、新闻稿与操作提示的语气；保留粗口和角色态度。
- 同步 16 段日记的逐行显示，保持原行槽、日期和分页；逐行宽度不超过对应旧段的最长行估算值。

## 版本与验证

版本号为 1.1，安装器门禁与清单一致。重编译后校验全部 10,202 对英文键与顺序、字典外数据、占位符、显示标记、换行标记和中文字体覆盖。
本轮补齐原包裁剪字体缺失的汉字，保留原有字形与字体度量；图片、视频硬字幕、脚本、房间和回退机制沿用原包。

全部10,202个翻译键完成本轮检查：9,836个键按9,506个完整英文分组逐条双语审校（同句不同译文同时查看），366个数字金额键逐项校验数值与单位。保留未需修改的译文。AI辅助审校记录、完整覆盖记录和第一轮历史稿均随项目保存。
外置SRT的25条中文已通读，保留原时间轴与译文；视频英文音轨、图像硬字幕及游戏内语境尚待验收。
游戏本体已提供，本版将安装并核验实际落盘文件。游戏内显示与剧情通关验收仍待完成，保留为候选版。v1.0.1的历史通关记录不迁移为本版结论。

## 安装与回退

完整解压后运行安装入口。已装旧包者先用对应旧包回退，再安装本版。详情见安装说明。
'''
 (PKG/'发布说明.md').write_text(release,encoding='utf-8')
 # Source and package audit hashes are kept outside the ZIP to avoid self-hash recursion.
 inventory=[{'path':p.relative_to(PKG).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(PKG.rglob('*')) if p.is_file()]
 dump(ROOT/'qa/package_files.json',inventory)
 zip_path=ROOT/'build'/f'{NAME}.zip'
 with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(PKG.rglob('*')):
   if p.is_file():
    info=zipfile.ZipInfo(NAME+'/'+p.relative_to(PKG).as_posix(),(2026,10,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
    z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(zip_path) as z:
  assert z.testzip() is None
  for item in inventory:assert sha(z.read(NAME+'/'+item['path']))==item['sha256']
 (ROOT/'build/SHA256SUMS.txt').write_text(sha(zip_path.read_bytes())+'  '+zip_path.name+'\n',encoding='utf-8')
 dump(ROOT/'qa/build_summary.json',{'package':zip_path.relative_to(ROOT).as_posix(),'zip_sha256':sha(zip_path.read_bytes()),'zip_bytes':zip_path.stat().st_size,'zip_crc_and_file_hashes':'passed','package_files':len(inventory),'tra_sha256':sha(rebuilt),'tra_bytes':len(rebuilt)})
 # Self-contained review UI: string values are escaped and inserted as text only.
 data=json.dumps(changes,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
 template='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Resonance v1.1 双语修订记录</title><style>body{font:16px/1.7 system-ui;margin:0;background:#111820;color:#dce6ee}main{max-width:1200px;margin:auto;padding:32px}h1{font-size:27px}input,select{background:#1c2935;color:white;border:1px solid #456;padding:10px;margin:8px 0;width:min(100%,600px);box-sizing:border-box}article{border:1px solid #34485a;background:#17232e;border-radius:10px;margin:16px 0;padding:18px;overflow-wrap:anywhere}p{white-space:pre-wrap;margin:6px 0}.old{color:#d7aa9a}.new{color:#8cddb7}.en{color:#a4bad0}.meta{font-size:13px;color:#9aafbf}button{padding:10px;background:#263f53;color:white;border:1px solid #5c7f9a;cursor:pointer}aside{background:#23313e;padding:15px;border-left:3px solid #cfba6f}</style><main><h1>Resonance · v1.1 双语修订记录</h1><aside>全量文本校对完成 · 游戏内显示与剧情验收待完成。全部改动保留英文、旧译、新译和来源编号。此页含剧情剧透。日记行键的英文是显示标识，可沿“依据编号”回查对应原文。</aside><p id="summary"></p><input id="q" placeholder="搜索英文、旧译、新译、编号或原因"><select id="filter"><option value="all">所有修订</option><option value="main">直接审定译文</option><option value="variant">同句显示变体</option><option value="journal">日记分行</option></select><p id="count"></p><div id="items"></div><button id="more">显示更多</button></main><script>const rows=__DATA__;let limit=60;const $=x=>document.getElementById(x);$('summary').textContent='本轮 '+rows.length+' 对键有修改；全部 10,202 对键已完成校对与结构校验（含 366 个数字金额键等值核验）。覆盖记录见项目报告。';function render(){const q=$('q').value.toLowerCase(),f=$('filter').value;const filtered=rows.filter(r=>(f==='all'||f==='journal'&&r.en.startsWith('RES_JOURNAL_')||f==='main'&&r.id===r.basis_id||f==='variant'&&r.id!==r.basis_id&&!r.en.startsWith('RES_JOURNAL_'))&&JSON.stringify(r).toLowerCase().includes(q));$('items').replaceChildren();for(const r of filtered.slice(0,limit)){const a=document.createElement('article');for(const [cls,value]of[['meta','#'+r.id+' · 依据 #'+r.basis_id+' · '+r.reason],['en','英文：'+r.en],['old','旧译：'+r.before],['new','新译：'+r.after]]){const p=document.createElement('p');p.className=cls;p.textContent=value;a.append(p)}$('items').append(a)}$('count').textContent='匹配 '+filtered.length+' 条，当前显示 '+Math.min(limit,filtered.length)+' 条';$('more').hidden=limit>=filtered.length}$('q').addEventListener('input',()=>{limit=60;render()});$('filter').addEventListener('change',()=>{limit=60;render()});$('more').addEventListener('click',()=>{limit+=60;render()});render();</script></html>'''
 (ROOT/'docs/双语修订记录.html').write_text(template.replace('__DATA__',data),encoding='utf-8')
 print(json.dumps({'changed_rows':len(changes),'counts':counts,'zip_bytes':zip_path.stat().st_size,'zip_sha256':sha(zip_path.read_bytes())},ensure_ascii=False))
if __name__=='__main__':main()
