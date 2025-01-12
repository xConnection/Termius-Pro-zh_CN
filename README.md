# Termius Pro zh-CN

## 简介

- 该项目是一个 Termius 补丁包教程，用于将 Termius 软件界面翻译为中文。

## 教程

### 脚本一键汉化

- 使用`python`脚本一键汉化。

1. 安装

    - 确保你已经安装了以下工具：
        - Python
        - `asar` 工具(用于处理 asar 文件)，可以通过 `npm install -g asar` 安装。

2. 运行脚本
    ```sh
    python lang.py
    ```

如果最后输出 `Replacement done.` 说明汉化完成。

### 手动汉化

如果没有`python`环境，可以手动汉化。

1. 前往 [releases](https://github.com/ArcSurge/Termius-Pro-zh_CN/releases) 下载对应版本的 `app.asar` 文件。
2. 找到 Termius 安装目录，通常位置为
    - **Windows**: `C:\Users\你的用户名\AppData\Local\Programs\Termius`。
    - **Linux**: `/opt/Termius`。
    - **MacOS**: `/Applications/Termius.app/Contents`。
3. 将下载的 `app.asar` 文件覆盖 `resources` 文件夹下的 `app.asar` 文件。
4. 如果你不想自动更新，请删除 `app-update.yml` 文件。

## 注意事项

- 该项目仅适用于本地学习和测试，不支持在线功能。
- 使用汉化包可能会影响 Termius 软件的正常更新。
- 在执行任何操作之前，请确保备份 Termius 的相关文件。

## 关于 `lang.py` 说明

### 功能

- **字符串替换**：根据提供的语言文件 `locales.txt` 或 `crack.txt` 替换 Termius 界面上的字符串。
- **文件搜索**：搜索指定的字符串，并显示包含这些字符串的文件路径。

### 参数说明

- `-replace` 或 `-R`: 根据 `locales.txt` 或 `crack.txt` 文件执行字符串替换操作。
- `-search` 或 `-S`: 搜索指定的字符串。例如：`-search "term1" "term2"`，在 Termius 的所有 JS 文件中搜索 `term1` 和 `term2` 同时存在的文件。
- `-css` 或 `-C`: 搜索或替换的包含css文件，默认不包含。例如：`-search "term1" "term2" -css` ，在 Termius 的所有 JS 和 CSS 文件中搜索 `term1` 和 `term2` 同时存在的文件。
- `-crack` 或 `-K`: 替换包含 `crack.txt` 文件，默认不包含。
### 目录结构

```
project/
├── crack.txt
├── locales.txt
└── lang.py
```

- `crack.txt`: 包含消除 Pro 相关的替换。
- `locales.txt`: 包含需要替换的语言字符串。
- `lang.py`: 主脚本文件。

## 声明

- 本仓库包括发布页内的所有文件仅供学习和交流，请勿用于任何非法用途，严禁二次出售，请在下载后的24小时内删除！如有侵权请联系删除！
- 本项目仅为社区贡献者个人行为，使用本补丁包可能存在风险，请用户谨慎决定是否安装。
- 用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。
- 本人对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害。