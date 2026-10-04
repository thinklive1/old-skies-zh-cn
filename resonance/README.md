# 共鸣 / Resonance 简体中文汉化 v1.1

本目录是 `resonance-zh-cn` 分支中的《共鸣》汉化项目，基于用户提供的 v1.0.1 正式版进行 AI 辅助双语校对。原汉化署名：**B站 up 主 那卡nakami**。原作者、游戏开发者、发行方与字体授权材料保留。

目前为 **全量校对候选版**：全部 10,202 个翻译键已检查，修改 1,497 个显示键。技术检查与实际安装文件核验通过；游戏内显示、完整谜题与剧情分支验收仍待完成。v1.0.1 的历史通关记录不作为 v1.1 的验收结论。

## 下载与安装

在 [releases 目录](releases)下载 `Resonance_zh-CN_v1.1_full-review_candidate.zip`，并使用同目录 `SHA256SUMS.txt` 核验文件。GitHub 文件预览页的 **Download raw file** 可下载完整补丁。

1. 退出游戏，完整解压补丁。
2. 已安装旧汉化时，先使用对应旧包的回退入口恢复原版。
3. 运行本包“安装汉化.bat”，选择包含 `Resonance.exe` 的游戏目录。
4. 保留游戏目录中的 `_Resonance_简中备份`。需要恢复时，退出游戏后运行本包“回退汉化.bat”。

安装器核验包内清单和文件哈希、备份实际原件，不读写个人存档。详细说明见补丁内“安装说明.txt”。

## 项目资料

- `source/`：原始双语字典、当前译文、明确修订输入、修改记录和第一轮历史稿。
- `docs/`：翻译规范、术语语境复核、可搜索的双语修订记录、字体授权与验收说明。双语修订记录含剧情剧透。
- `qa/`：全量校对覆盖、结构与字体检查、安装回退测试、实际安装及公开交付报告。
- `tools/`：修订应用、构建、字体处理、安装测试与正式发行门禁。
- `baseline/source_lock.json`：原 v1.0.1 的 144 个文件哈希锁定清单。
- `releases/`：已验证的完整候选补丁及 SHA256 校验文件。

## 编辑与构建

常规构建需要 Python 3.9 或更新版本，使用标准库。构建前准备原 v1.0.1 汉化包；导入工具会逐一核对全部锁定哈希。

```powershell
cd resonance
python tools/prepare_base.py --original-zip "原版汉化包.zip"
# 也可使用 --original-dir "原版汉化包解压目录"
python tools/apply_review.py
python tools/build.py
```

编辑 `source/manual_revisions.tsv` 时，应同步更新 `source/revision_decisions.json` 的同条新译，保留英文键与解谜信息。新增文本修改需要重新审校和检查。

字体补齐结果已保存在 `source/fonts`。重建字体才需要 `fontTools==4.60.1`，同源字体与许可见 `source/font_upstream`。Windows PowerShell 5.1 的安装回退测试见 `tools/test_install.ps1`，使用新的专用测试目录。`tools/release_gate.py` 要求真实游戏验收报告后才允许正式发行。

本目录未附原 v1.0.1 的完整资源快照。原包导入后位于 `baseline/v1.0.1`，不纳入 Git。补丁中沿用的图片、视频、房间和脚本与本轮修订范围见 `docs/发布与验收.txt`。不同材料的权利归属依照原署名与授权说明。
