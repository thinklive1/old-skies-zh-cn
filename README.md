# Old Skies《往昔天穹》简体中文汉化 v1.1

基于那卡nakami制作的 v1.0 简体中文汉化进行文本修订，目标是减少直译、生硬句式与语义错误，并统一人物、时间旅行设定及界面术语。

**当前版本：v1.1 首轮审校候选版。** 已核读 19,402 条文本，修订 3,157 条。录音花絮、开发者解说及其标题保留 v1.0 原文。安装与文件检查通过，游戏画面及全流程验收尚未记录为通过。

## 下载与安装

到 [Releases](https://github.com/thinklive1/old-skies-zh-cn/releases) 下载完整补丁 ZIP，解压后运行“安装汉化.bat”。详细操作与恢复方式见 [安装说明](docs/INSTALLATION.md)。

## 项目文件

- `source/translations.v1.1.json`：可编辑双语文本与逐条审校状态。
- `source/original.v1.0.json`：锁定的 v1.0 原译，保留英文键和条目顺序。
- `source/font_common.json`：字体覆盖检查使用的字形范围。
- `docs/`：文风、术语、修改记录、安装说明和语境回查点。
- `review/`：分段修改记录及花絮/解说保留清单。最终译文以 source 中的文件为准，历史修改记录不应直接全部重新套用。
- `reports/changes.json`：最终逐条修改对照。
- `reports/qa.json`：全量技术检查结果。
- `reports/installation.json`：安装后校验记录，已移除本机路径。
- `tools/`：译文合并及 TRA 编译、校验和打包工具。
- `upstream/v1.0/`：本地构建依赖目录，使用原 v1.0 补丁或本仓库 Release 包导入。

## 本地构建

需要 Python 3，仅使用标准库。先下载 Release 补丁 ZIP，在仓库根目录导入构建依赖：

```powershell
python -X utf8 tools/prepare_base.py --patch-zip "下载的补丁.zip"
```

导入时会重建并校验锁定 v1.0 文本的 SHA256，再执行：

```powershell
python -X utf8 tools/build.py --candidate --check-only
python -X utf8 tools/build.py --candidate --build-tag local-r1
```

构建结果保存在 build/。脚本会检查英文键与顺序、配音编号、占位符、AGS 换行标记、新增字形、TRA 往返解析和非字典区块。已有构建目录不会被覆盖。正式构建仍要求真实的游戏内验收记录。

## 校对与反馈

修改中文 zh，保持 id 和英文 en 不变。文风见 [STYLE](docs/STYLE.md)，术语见 [TERMS](docs/TERMS.md)。少数依赖画面、语音或英语双关的条目见 [语境回查记录](docs/CONTEXT_CHECKS.md)。

反馈时请提供章节、场景、原句或截图，以及希望调整的理由，以便定位文本和保留修改记录。

## 署名与授权材料

原 v1.0 汉化：B站up主 **那卡nakami**。原汉化的署名、图片、字体授权和安装逻辑予以保留；v1.1 是基于该版本的文本修订项目。

游戏及原汉化相关权利归各自权利人，本项目不代表原作者或游戏开发商。字体授权随补丁 ZIP 提供，导入后见 upstream/v1.0/字体授权_OFL.txt；未给游戏资源或原译文另行添加通用开源许可。
