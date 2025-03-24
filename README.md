# Termius 中文汉化及功能增强脚本

## 🎉 简介

Termius 汉化脚本

## ✨ 功能特性

- **一键汉化** - 自动化界面汉化
- **试用功能激活** - 解锁高级特性
- **多平台支持** - Windows/macOS/Linux
- **安全机制** - 自动备份

## 🚀 快速开始

### 📦 前置要求

- Python
- Node.js (用于安装asar)

```bash
npm install -g asar
```

### 🧑‍💻 基础使用

```bash
# 默认执行汉化操作
python lang.py
```

### 🪄 高级功能

```bash
# 汉化+试用+样式修改
python lang.py --localize --trial --style

# 仅激活试用功能
python lang.py --trial

# 还原到初始状态
python lang.py --restore

# 搜索特定字符串
python lang.py --find "term1" "term2"
```

## 🔬 参数详解

| 参数                | 简写   | 功能说明     | 示例                                  |
|-------------------|------|----------|-------------------------------------|
| `--localize`      | `-l` | 汉化操作(默认) | `python lang.py`                    |
| `--trial`         | `-t` | 激活试用功能   | `python lang.py -lt`                |
| `--skip-login`    | `-k` | 跳过登录验证   | `python lang.py -lk`                |
| `--style`         | `-s` | 样式修改     | `python lang.py -ls`                |
| `--restore`       | `-r` | 还原操作     | `python lang.py -r`                 |
| `--find <关键词...>` | `-f` | 多条件联合搜索  | `python lang.py -f "term1" "term2"` |

## 📂 规则文件结构

```markdown
rules/
├── trial.txt      # 试用功能规则(-t/--trial时加载)
├── localize.txt   # 汉化规则(-l/--localize时加载)
├── skip_login.txt # 登录跳过规则(-k/--skip-login时加载)
└── style.txt      # 样式修改规则(-s/--style时加载)
```

## 🤷 手动汉化

如果没有相关环境，可以手动汉化。

1. 前往 [releases](https://github.com/ArcSurge/Termius-Pro-zh_CN/releases) 下载对应版本的 `app.asar` 文件。
2. 找到 Termius 安装目录，通常位置为:
    - **Windows**: `C:\Users\你的用户名\AppData\Local\Programs\Termius`。
    - **Linux**: `/opt/Termius`。
    - **MacOS**: `/Applications/Termius.app/Contents`。
3. 将下载的 `app.asar` 文件覆盖 `resources` 文件夹下的 `app.asar` 文件。
4. 如果你不想自动更新，请删除 `app-update.yml` 文件。
5. 最后，如果没有想要的版本，可 **fork** 本项目，在仓库的 `Settings > Secrets and variables > Actions > Variables` 中定义变量:
   - **Name**: RELEASE_LIST
   - **Value**: l,lk,lt
   - 默认`l,lk,lt`，代表生成三个版本，l为汉化，lt为汉化+试用，lk为汉化+跳过登录。可自行修改，通过逗号分隔。

## 🔔 注意事项

- 该项目仅适用于本地学习和测试，不支持在线功能。
- 使用汉化包可能会影响 Termius 软件的正常更新。
- 在执行任何操作之前，请确保备份 Termius 的相关文件。

## 📜 免责声明

- 本仓库包括发布页内的所有文件仅供学习和交流，请勿用于任何非法用途，严禁二次出售，请在下载后的24小时内删除！如有侵权请联系删除！
- 用于测试和学习研究，禁止用于商业用途，不能保证其合法性、准确性、完整性和有效性，请根据情况自行判断。
- 本人对任何问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害，使用即表示知晓风险。
- 保留随时终止项目的权利。