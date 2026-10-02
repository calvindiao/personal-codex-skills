# 安装、更新与恢复

运行命令的主机和用户，应与实际运行 Codex 的主机和用户一致。先安装 Git 和 Python 3.10+。

## 已有安装

保留现有 clone 和 skill 路径，先在 clone 中执行 README 的更新命令。不要为了使用新目录示例而再次安装同名 skill。

早期安装可能把整个仓库 clone 到 `~/.agents/skills`，也可能把单个 skill 链接到 `~/.codex/skills`。本仓库保留顶层 skill 路径以兼容这些安装。当前官方推荐的个人 skill 目录是 `~/.agents/skills`；同名 skill 出现在多个发现目录时，可能重复出现，应先确认实际加载来源。[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)

如果旧安装是复制目录，Git 拉取只更新 clone，不会更新副本。比较并保留副本中的修改后，更新副本或改为链接；不要直接覆盖未知内容。

## 新主机：clone 到工作目录

选择一个稳定的目录保存仓库；下例使用 `~/src`。仓库与个人 skill 发现目录分开，便于同时安装其他来源的 skill。

macOS / Linux：

```sh
mkdir -p "$HOME/src"
git clone https://github.com/calvindiao/personal-codex-skills.git "$HOME/src/personal-codex-skills"
cd "$HOME/src/personal-codex-skills"
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME\src" | Out-Null
git clone https://github.com/calvindiao/personal-codex-skills.git "$HOME\src\personal-codex-skills"
Set-Location "$HOME\src\personal-codex-skills"
```

任一步失败时，先处理该错误，再继续后续步骤。

## 安装所需的 skill

以下命令从 clone 根目录运行，只链接 `evidence-led-engineering`。如果目标已存在，先查看它是否已指向此仓库。

macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
skill_target="$HOME/.agents/skills/evidence-led-engineering"
if [ -e "$skill_target" ] || [ -L "$skill_target" ]; then
  printf 'Existing installation; inspect before changing: %s\n' "$skill_target"
else
  ln -s "$PWD/evidence-led-engineering" "$skill_target"
fi
```

Windows PowerShell 使用目录 junction：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
$skillSource = Join-Path (Get-Location) "evidence-led-engineering"
New-Item -ItemType Junction -Path "$HOME\.agents\skills\evidence-led-engineering" -Target $skillSource
```

Codex 支持链接的 skill 目录。链接后，Git 更新会直接更新其来源；不要移动或删除 clone。无法创建链接时，可以复制整个 skill 包，但以后需要显式更新副本。[发现与链接规则](https://learn.chatgpt.com/docs/build-skills)

## 安装共享沟通规则

macOS / Linux：

```sh
python3 scripts/sync-instructions.py
python3 scripts/sync-instructions.py --check
```

Windows PowerShell：

```powershell
py -3 scripts/sync-instructions.py
py -3 scripts/sync-instructions.py --check
```

没有 `py` 启动器时使用 `python`。脚本读取 `CODEX_HOME`；未设置时使用当前用户的 `.codex` 目录。可用 `--codex-home /path/to/profile` 明确指定目标。只复制沟通规则，不复制登录信息、MCP 配置或其他主机配置。

| 退出码 | 含义 | 下一步 |
| --- | --- | --- |
| `0` | 安装完成，或共享内容已匹配当前 clone | 新会话中确认加载 |
| `1` | `--check` 发现缺少安装或内容不同 | 先确认 Git 版本，再运行安装命令 |
| `2` | 文件、权限、override、链接或标记有问题 | 按具体错误检查后重试 |

活动的 `AGENTS.override.md` 会优先于 `AGENTS.md`。同步脚本对此报错；根据该主机的需要，把共享规则合并进 override，或停用不再需要的 override 后再安装。手动合并进 override 不属于脚本管理范围。[全局指令加载顺序](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## 确认生效

1. 在各 clone 查看 `git rev-parse HEAD`，确认使用预期的 Git 版本。
2. 运行 `--check`，比较输出的规则 SHA-256。它检查共享规则，不要求各主机的其他指令相同。
3. 新开 Codex 对话，让它列出已加载的指令来源，确认沟通规则，并确认需要的 skill 可用。

项目指令可能覆盖全局指令中的冲突项。终端、桌面应用或远程服务也可能使用不同的用户或 `CODEX_HOME`，应检查实际执行环境。Windows 与 WSL 的用户目录分别管理。

## 更新、回退与移除

更新：在 clone 中 `git pull --ff-only`，确认成功后重新运行规则同步及检查命令。需要固定版本的主机，可 checkout 已检查过的提交后再同步；升级时再选择新版本。

回退规则：安装器修改已有文件前，会打印 `AGENTS.md.backup-<时间戳>` 的路径。查看备份与当前文件的差异，保留安装后新增的主机规则，再恢复所需内容。若从未有过文件，首次安装不会产生备份。

移除共享规则：从全局文件中删除带 `personal-codex-skills:communication` 标记的完整区块，保留区块外内容。移除 skill 时删除对应安装链接或副本；保留需要继续使用的仓库来源。

避免同时用编辑器或其他同步程序修改同一个全局文件。脚本会尽力检测并发变化并原子替换文件，但不是多个写入程序之间的事务协调器。
