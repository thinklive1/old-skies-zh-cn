Resonance 简体中文汉化 v1.1 项目
基线：用户提供的v1.0.1正式版。日期：2026-10-03（Asia/Shanghai）
当前状态：全量文本校对完成，已构建候选包并完成本机实际安装；游戏内显示及剧情通关验收待完成。

交付入口
build/Resonance_简体中文汉化_v1.1_全量校对候选版.zip：本轮最新完整补丁。
docs/双语修订记录.html：可搜索的英文、旧译、新译及依据编号，含剧情剧透。
docs/翻译规范.txt：用户认可的文风、角色与术语基准及解谜保护要求。
docs/发布与验收.txt：实际完成的检查与剩余游戏内验收项目。
qa/actual_install.json：用户指定游戏目录的安装核验结果。

完整校对
10,202个翻译键全部检查完毕。9,836个键按9,506组完整英文逐条双语审校；同句的中文变体一并查看。
另外366个数字金额键逐项核验数值和比索单位。
1,497个显示键有修改：1,308条直接修订、86条同英文显示变体、103条日记行键。
其余8,339个键查看后保留，366个金额键核验后保留；未审键为0。
本轮新增直接修订又完整对照英文复核，并纠正错位、漏句；记录在qa/revision_second_pass.json。
25条外置SRT通读中文并检查时间轴，保留原译；尚未对照英文音轨与硬字幕。
图片、视频硬字幕、游戏脚本和房间沿用原包，游戏内语境和排版仍须实际验收。
上述是AI辅助双语校对，不冒称原汉化作者已审定或已完成本版通关。

项目文件
source/original.v1.0.1.json：原始双语字典及稳定编号。
source/manual_revisions.tsv：编号和新译两列，是当前直接修订的输入。
source/revision_decisions.json：与直接修订对应的英文键，防止编号漂移。
source/translations.v1.1.json：全量当前译文、原译、每条校对状态与依据编号。
source/change_log.json：实际修改记录。
source/history/first_pass：第一轮文本润色历史稿；build中第一轮候选ZIP也保留。
qa/full_review_coverage.json：真实分批审校覆盖与输入哈希，金额检查单独记录。
qa/text_validation.json：译文控制信息、回编、字体覆盖与日记同步检查。
qa/font_expansion.json：十个字体逐项补字及旧字形、宽度和全局度量的验证。
qa/installer_tests.json与installer_tests_final_zip.json：构造夹具的安装回退测试，非游戏内测试。
qa/build_summary.json与final_zip_verification.json：最终ZIP与文件哈希验证。
baseline：原v1.0.1完整副本及144个文件的SHA256锁定清单。

编辑与构建
Python3.9或更新版本；常规构建仅使用标准库。
1. 编辑source/manual_revisions.tsv，同时更新revision_decisions.json中的同条新译；英文键必须与原始字典完全一致。
2. python tools/apply_review.py
3. python tools/build.py
4. Windows PowerShell5.1运行tools/test_install.ps1，使用新的专用WorkRoot测试目录。
同句显示变体按完整英文同步；不同英文不做全局中文替换。日记按原段精确匹配并在原行槽内重排。
完整校对记录是本轮实际查看的记录，不自动把后续新增源文本当作已审。
source/fonts保存补齐后的字体。仅在新增汉字超出覆盖时重建字体：fontTools==4.60.1，python tools/add_fonts.py。
同源字体、发行物哈希和完整许可保存在source/font_upstream；字体说明在docs/字体补字说明.txt。
ZIP使用固定文件时间与顺序。SHA256SUMS.txt可核验本轮完整候选包。
正式门禁python tools/release_gate.py仍会因缺少实际游戏内验收报告而拒绝正式发行。

安装与回退
已安装至<游戏目录>，29个受管文件与原件备份核验通过，105项图片匹配成功；记录见qa/actual_install.json及docs/交付与安装记录.txt。
安装器备份实际原件并核验包内清单和文件哈希，不读写个人存档。
保留游戏目录_Resonance_简中备份，用本轮候选包中的回退汉化.bat恢复安装前文件。
安装后核验不等于游戏内显示、完整谜题与分支通过。
旧版产生的备份必须由对应旧包回退，不直接跨包覆盖。

署名
保留原包“简体中文汉化：B站up主 那卡nakami”及原作者、发行方署名。
原v1.0.1、第一轮候选包和本轮候选包分别保存。项目不含完整游戏或私人存档。
