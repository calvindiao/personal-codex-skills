# 维护指南

先判断要改变什么，再进入相应文件。通常不需要同时修改所有层。

| 变化 | 修改位置 | 相关检查 |
| --- | --- | --- |
| 沟通偏好 | `instructions/AGENTS.md` | 含义是否保留；临时目录安装与检查 |
| skill 触发范围或任务指导 | 对应包的 `SKILL.md` | 格式、引用、代表任务和误触发样本 |
| 某种模式才需要的材料 | 包内 `references/` | 入口可发现；引用有效 |
| 重复且需要确定执行的操作 | 包内 `scripts/` | 在隔离输入上运行，检查实际输出 |
| 同步和文件操作 | 仓库 `scripts/`、`tests/` | 保留原内容、冲突、重复运行和恢复 |
| 安装步骤与目录约定 | README、`docs/`、根目录 `AGENTS.md` | 命令、链接、现有安装的迁移影响 |

## 添加或修改 skill

新包放在顶层 `<skill-name>/`。名称与 frontmatter 的 `name` 一致；本仓库建议使用小写英文字母、数字和连字符，方便跨平台阅读路径。入口写明能做什么、何时适用；近似但不适用的任务只在确实容易误触发时说明。

```yaml
---
name: explain-query-plans
description: Explain database query plans when diagnosing a slow query or comparing an index change.
---
```

正文提供目标、关键判断和必要约束。模型已有的通用知识不必重复。只有出现明确用途时，再加脚本、示例、引用或素材；引用应从入口直接可达，包复制到其他位置后仍可使用。

不要把安装路径、账户、项目私有数据或某台机器的配置写入可复用包。客户端特有字段需要注明兼容范围。不要未经检查就复制第三方 skill 的全文或默认其许可证适用。

## 运行确定性检查

使用 Python 3.10+ 创建独立的开发环境。已有 `.venv` 时可跳过创建步骤。macOS / Linux：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe scripts/validate.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

验证器检查实际 skill 包的 YAML、名称、必需字段与入口正文中的本地 Markdown 引用。它不检查原始 HTML 链接、页内锚点或远端页面，也不判断事实和任务质量。目录、篇幅和文风建议不作为机械评分。

同步测试在临时目录中运行，覆盖保留已有规则、重复执行、备份、覆盖文件、符号链接、CRLF 和并发变化。运行时同步仍只依赖标准库。CI 矩阵与版本见 `.github/workflows/checks.yml`；报告结果时引用对应提交与运行，不把配置了 CI 当成 CI 已通过。

## 检查 skill 的实际行为

修改触发或任务指导时，选择少量有代表性的任务，加入容易误触发的相近任务。关注任务是否完成、证据是否匹配、是否增加无用步骤；无需因文字润色重跑昂贵评测。

以 `evidence-led-engineering` 为例：

| 样本 | 应观察什么 |
| --- | --- |
| “排查重复提交，复现后修好” | 找到可观察的失败和原因，修复后重复相关检查 |
| “只审查原因，暂时别改文件” | 给出有依据的调查结果，尊重只读范围 |
| “本地测试通过了，能证明线上恢复了吗？” | 区分本地测试与线上行为，并查找相应证据 |
| “把 README 中一个拼写错误改掉” | 直接完成简单修改，不引入完整调查流程 |
| “解释一下 Git branch 是什么” | 普通解释，不要求先扫描仓库或运行测试 |
| “已授权修复并发布，继续完成” | 沿已授权范围完成工作，不由 skill 增加重复确认 |

需要比较效果时，用同一输入分别运行旧版/新版或有/无 skill。记录日期、模型、skill 提交、输入、实际结果和判断理由。格式检查或单次 agent 自评不能证明普遍改善。使用隔离样本；真实发布、通信或收费调用仍按当前任务的授权执行。

## 发布与兼容性

合入和发布方式随任务选择。发布前确认相关检查、差异和已有安装的兼容性，记录可定位的 Git 提交。稳定路径或 CLI 发生变化时，在安装指南写清迁移和回退方式。

开发依赖版本固定在 `requirements-dev.txt`，CI action 固定到提交。更新它们时运行相关测试，并保留 Python 最低版本与三种操作系统的 CI 覆盖。

共享规则更新后，各主机需要拉取并重新运行安装器；链接的 skill 随 clone 更新，复制的 skill 需要同步副本。根目录 `AGENTS.md` 和人类文档不应被整体安装为全局指令。
