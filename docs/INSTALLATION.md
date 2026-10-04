# 安装与恢复

从 Releases 下载 v1.1 补丁 ZIP，完整解压后运行“安装汉化.bat”，按提示选择包含 OldSkies.exe 的游戏目录。安装前关闭游戏。

也可在 PowerShell 中明确指定目录：

```powershell
& '.\安装汉化.ps1' -GameDir '你的 Old Skies 游戏目录'
```

安装器校验补丁清单、备份原配置文件与原始图片数据，再写入补丁，并将语言设为 Chinese。

如需恢复英文版，在同一个完整补丁目录运行“卸载汉化.bat”，或执行：

```powershell
& '.\卸载汉化.ps1' -GameDir '你的 Old Skies 游戏目录'
```

备份保存在游戏目录下的 OldSkies_Chinese_Backup。图片使用逐跨度备份与恢复方式，没有复制整份游戏数据文件。请保留备份目录。

2026-10-03 安装验证结果：40 个补丁文件哈希一致，25 处图片写入成功，25 份原始图片备份哈希一致，两个配置文件仅更改语言，OldSkies.exe 未修改。完整检查见 reports/installation.json。游戏画面和全流程验收尚未记录为通过。
