# Technobabylon 简体中文汉化工程

当前版本：**1.0.0-rc.1，公开验收候选**。全文翻译和第二轮校对已完成，技术检查通过；游戏中的画面与正常游玩由用户验收。候选的完整性与用户视觉验收分别记录，不把离屏测试当作完整通关。

适配用户持有的 Steam build 24559207，原版 AGS 3.6.1.35，游戏 UID 1186933。原 EXE SHA-256 为 `8ed8f2312aed87cb6f6c520dd83be6afc9c93976f6ab004fca7e772b2411a44d`。安装器拒绝其他版本及未知外置主数据。

## 下载候选补丁

本项目位于 [游戏汉化仓库](https://github.com/thinklive1/old-skies-zh-cn) 的 `technobabylon-zh-cn` 独立分支。
到 [Technobabylon 1.0.0-rc.1 Release](https://github.com/thinklive1/old-skies-zh-cn/releases/tag/technobabylon-v1.0.0-rc.1) 下载 `Technobabylon_zh_CN_1.0.0-rc.1.zip`。
解压 ZIP、关闭游戏后，执行包内 `安装说明.txt` 中的安装命令。自动生成的 Source code ZIP 是工程源码，不是可直接安装的补丁。

此版本已完成全文翻译、二轮校对和技术安装验证；实际画面与全流程验收仍为待确认，因此标记为预发布候选。

## 文本范围与校对

英文基线有 13,118 个独立键、20,207 个来源引用、86 个房间。完成 11,984 条中文译文，全部具有绑定原文与最终译文哈希的第二轮校对凭据；未译与待二读均为 0。另有 243 条明确保留原文、891 条明确排除，每项保留理由，均不计入中文完成数量。开发者解说沿用英文；作者和演员署名、账号、程序控制键及解谜所需字母按实际用途保留。密码、数字、语音标记、格式符与换行单独校验。

`docs/TERMS.json` 保存本项目锁定的译法及上下文依据。原作没有提供汉字的姓名与虚构名称属于项目翻译选择，不宣称官方中文。每个修改批次保存在 `review/batches`，范围审计在 `review/scope`，二轮凭据在 `review/receipts`。修改译文会使旧凭据失效，必须重新校对。

## 工程目录

| 路径 | 用途 |
| --- | --- |
| `project.json` | 版本、适配与候选状态 |
| `source/catalog.en.json` | 不可覆盖的英文基线与来源定位 |
| `source/baseline.json` / `source/game.json` | 原版资源校验和游戏身份 |
| `source/runtime-keys.json` | 精确运行时修正配方、结构与校验值 |
| `translation/*.zh-CN.json` | 88 个译文分片 |
| `docs/STYLE.md` / `docs/TERMS.json` | 文风与术语 |
| `review/batches` / `review/scope` / `review/receipts` | 翻译、范围与校对审计 |
| `review/issues` / `review/qa` | 问题、修复和验证证据 |
| `review/acceptance.json` | 独立记录用户视觉验收 |
| `tools` | 提取、构建、检查、安装和回滚 |
| `fonts` | 中文字形来源、固定版本和许可 |
| `build/release` | 本机生成的候选文件，不纳入 Git |

## 提取与构建

Python 3.10+、.NET 6 SDK/Runtime，实测 SDK 6.0.414。字体依赖固定在 `requirements.txt`。提取器采用 [AGSUnpacker](https://github.com/adm244/AGSUnpacker) 的固定提交 `3971a5de79c8b45050ec8ddf742bec1a0bb6e2f5`，Windows-1252 解码与原游戏一致。

```powershell
python -m pip install -r requirements.txt
pwsh -File tools/bootstrap_extract.ps1 -GameExe "D:\software\steam\steamapps\common\Technobabylon\Technobabylon.exe" -WorkDir ".\work"
python tools/check.py --assets .\work\assets --release
```

网络受限时，用 `-NuGetSource <本地依赖目录>` 指定离线源，`-SdkVersion` 仅用于已验证的替代 SDK。已有项目不可重跑初始导入覆盖译文。

构建会检查源基线、全部格式符、二轮凭据、发行阻断问题与技术门槛。输出原生 UTF-8 TRA、8 个外置字体、从本机原版生成的外置 `game28.dta`、构建清单和字体检查报告。TRA 原文匹配采用 `.1252`，目标文本为 UTF-8；编译后逐键反解核对。英文解说与重音文本的编码桥接另计，不算中文翻译。

## 运行时修正

补丁不改 EXE、语音或音乐。外置主数据经过精确原版大小与 SHA-256 检查，按三个有记录的问题生成：

1. 两条剧情与解说共享键仅在 Dialog 71 的原字符串池改末尾标点，让剧情映射中文、解说原键映射英文。
2. 五个玩家列表控件启用原引擎的绘制翻译标志。联系人返回给脚本的原始字符串仍保持原文，避免破坏字符串比较。
3. 原邮件与新闻滚动脚本依赖英文空格，长中文可触发 150001 次循环保护。中文模式采用 UTF-8 字符和实际字体 0 的像素宽度分行，单行不超过 260 像素，并处理 `[` 显式换行；未启用翻译时仍执行原英文路径。

第三项仅替换原代码中的两个源行入口（四个整数单元），追加有界辅助代码，保留原字符串池、全局数据、导出、旧指针和旧修正表。独立 C# 重提取核对全部 20,207 个原引用，只有两条指定剧情引用改为运行时别名；新增四个明确声明的原有邮件标题／分隔线引用。原始英文语义目录和稳定 ID 均保持不变。

## 字体与验证

7 个原 TTF 保留英文轮廓和度量，追加中文字符；字体 3 从 WFN 改为 TTF，中文来源是 [Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font) 2026.09.25，缺字由固定版本的 Noto Sans SC 400 补齐，OFL 许可随项目保存。连续轮廓描边通过覆盖检查。所有当前 TRA 目标字符均有字形。

实际 3.6.1.35 引擎在带标记的隔离副本加载候选，并由已安装配置选中中文，加载全部 8 个字体，进入启动房间，再逐文件回滚核对。原游戏目录与真实存档不参与隔离测试。

`probe_text_layout.py` 将全部 263 个超过 90 字符的非语音正文分别作为新闻及邮件测试，共 526 次列表检查；实际引擎验证每行宽度和分行前后字符数量。另检查 40 个字体 3 控件的实际文字宽度。`probe_scrollers.py` 对指定中文正文、主题和新闻条目进行值检查。探针代码只用于隔离副本，回滚前先恢复安装候选，不进入补丁。

```powershell
python tools/pilot_smoke.py "<带标记的隔离副本>" --release
python tools/probe_scrollers.py "<隔离副本>" "<scope-metadata.json>" --release
python tools/probe_text_layout.py "<隔离副本>" "<scope-metadata.json>" --release
```

这些检查证明资源加载、配置选中、文本处理、宽度和回滚链路。实际可见画面、完整游玩和 Steam 成就仍由用户确认，状态记录在 `review/acceptance.json`。

## 安装与回滚

先关闭游戏。安装器核对游戏与构建文件，原文件逐字节备份，暂存写入后替换，最后核对全部校验值；失败时恢复已写文件。安装范围为 TRA、8 个 TTF、外置主数据及 `acsetup.cfg` 的翻译选择，共 11 项。

```powershell
python tools/install.py install "D:\software\steam\steamapps\common\Technobabylon" --dry-run
python tools/install.py install "D:\software\steam\steamapps\common\Technobabylon"
python tools/install.py rollback "<游戏目录>\_Technobabylon_zh_CN_backup\<备份编号>"
```

备份包含原文件和原本不存在的状态。回滚拒绝覆盖安装后被另行修改的文件，并支持旧十文件与当前十一文件备份。正式安装结果另存 `review/qa/installed-verification.json`，不把候选构建成功当作实际安装完成。

## 来源与权属

原游戏及其资源属于 Technocrat Games / Wadjet Eye Games 和相关作者。EXE、语音、音乐、主数据及房间二进制不纳入 Git。候选包由已校验的原版资源生成，只包含汉化所需的翻译、派生字体与外置脚本数据，使用时须拥有原游戏。格式核对参考 [AGS v3.6.1.35](https://github.com/adventuregamestudio/ags/tree/v3.6.1.35) 和 [官方翻译文档](https://adventuregamestudio.github.io/ags-manual/Translations.html)。本分支是已完成本地安装验证的公开快照，来源提交及报告路径清理方式见 `docs/PUBLICATION.md`。
