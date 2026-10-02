# Personal Codex skills

[![Checks](https://github.com/calvindiao/personal-codex-skills/actions/workflows/checks.yml/badge.svg)](https://github.com/calvindiao/personal-codex-skills/actions/workflows/checks.yml)

保存可复用的 agent skills 和个人沟通规则，让不同项目、不同主机上的 Codex 使用同一份来源。

这里的 skill 提供任务所需的判断依据；沟通规则保持简短。按任务需要加载内容，保留 agent 选择方法的空间。

## 这里有什么

| 内容 | 用途 | 何时读取 |
| --- | --- | --- |
| [Evidence-led Engineering](evidence-led-engineering/SKILL.md) | 用可观察的行为判断调查、修改和发布检查是否完成 | 需要实际证据的工程任务；跳过简单修改 |
| [沟通规则](instructions/AGENTS.md) | 回答先行、术语一致、保留条件和不确定性 | 安装后作为 Codex 的全局指令加载 |
| [仓库维护入口](AGENTS.md) | 告诉维护此仓库的 agent 应该改哪里、检查什么 | 在这个仓库工作时 |

`SKILL.md` 使用开放的 Agent Skills 格式。当前安装说明与全局规则同步工具面向 Codex；Claude 等客户端的安装位置和扩展字段需要按各自文档处理。

## 已经安装过：更新并检查

进入本仓库的现有 clone。先确认 Git 拉取成功，再运行同步脚本。

macOS / Linux：

```sh
git pull --ff-only
python3 scripts/sync-instructions.py
python3 scripts/sync-instructions.py --check
```

Windows PowerShell：

```powershell
git pull --ff-only
py -3 scripts/sync-instructions.py
py -3 scripts/sync-instructions.py --check
```

没有 `py` 启动器时，可用已安装的 `python`。运行环境为 Git 和 Python 3.10+；同步脚本无需第三方 Python 包。

如果 skill 目录链接到这个 clone，拉取后即可使用新内容；如果以前复制过 skill，需要更新那份副本。全局沟通规则需要运行同步脚本。安装或更新后，新开 Codex 对话确认已加载。

**首次安装或新增主机：** 按[安装、迁移与恢复指南](docs/install.md)操作。它也覆盖已有 skill 目录、Windows、WSL、远程主机和自定义 `CODEX_HOME`。

## 同步工具会做什么

- 在全局 `AGENTS.md` 中添加或更新一个带标记的沟通规则区块。
- 保留区块外的主机规则，并在修改已有文件前保存带时间戳的备份。
- 检查模式只读。它检查安装内容是否与当前 clone 一致，并输出规则的 SHA-256。
- 发现活动的 override、无关符号链接、损坏标记或同步期间的文件变化时，报告问题。

共享区块由仓库管理。修改共享规则请编辑 `instructions/AGENTS.md`；主机特有规则放在区块外。同步不是后台服务，需要在各主机上显式运行。

文件一致、Codex 已加载、任务效果变好，是三项不同的检查。脚本负责第一项；后两项需要新会话和实际任务确认。

## 目录结构

```text
AGENTS.md                       仓库维护入口，不安装为全局规则
README.md                       人类阅读入口
instructions/AGENTS.md          共享沟通规则的唯一来源
evidence-led-engineering/        独立的 skill 包，保留现有安装路径
  SKILL.md                      适用范围与任务指导
  agents/openai.yaml            Codex 的可选界面元数据
docs/                           安装、设计理由与维护说明
scripts/                        显式运行的同步和结构检查工具
tests/                          隔离文件系统测试
.github/workflows/checks.yml     macOS、Linux、Windows 的 CI 检查
```

新增 skill 使用同级的 `<skill-name>/SKILL.md`。只有实际需要时，才在包内添加 `references/`、`scripts/` 或 `assets/`。现有 skill 保持短小、自包含，无需额外路由层。

## 修改与验证

普通使用只需安装或更新。修改结构、脚本或 skill 时，按[维护指南](docs/maintaining.md)选择与改动相符的检查。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

这是 macOS / Linux 的开发命令；Windows 命令见[维护指南](docs/maintaining.md#运行确定性检查)。结构检查使用 PyYAML 和 CommonMark 解析库；它们不是同步脚本的运行依赖。测试使用临时目录，不访问真实账户或修改真实 Codex 配置。

CI 检查格式、引用和脚本行为，不替代 skill 的实际任务评测。[设计说明与来源](docs/design.md)记录了采用 OpenAI、Anthropic 和 Agent Skills 指导的理由，以及兼容性边界。
