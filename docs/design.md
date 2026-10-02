# 设计与来源

设计目标是稳定复用、容易发现和按需读取。这里记录的是本仓库的选择，不是给所有任务追加一套固定流程。

## 内容分工

| 层 | 来源 | 使用方式 |
| --- | --- | --- |
| 个人沟通偏好 | `instructions/AGENTS.md` | 安装到各主机，保持少量跨任务规则 |
| 任务能力 | 顶层 `<skill-name>/SKILL.md` | 通过名称与描述发现，适用时读取正文 |
| 本仓库维护 | 根目录 `AGENTS.md` | 提供维护导航，不安装到全局 |
| 人类操作说明 | README 与 `docs/` | 安装、排错或修改设计时查阅 |
| 确定性工具 | `scripts/` | 显式运行文件同步与结构检查 |

skill 目录本身是事实来源，检查工具扫描实际的 `SKILL.md`。不另建重复登记名称、描述和路径的注册表。Codex 的界面元数据保存在包内 `agents/openai.yaml`，不混入通用任务指导。

## 稳定路径与更新边界

保留顶层 skill 目录，因为已有安装可能通过符号链接或 junction 指向这些路径。移动目录需要明确的迁移步骤和安装验证，不能只让仓库内部链接通过检查。

Git 负责版本传递；安装脚本负责更新全局规则。共享区块归仓库管理，区块外内容归主机管理。`--check` 确认与本地 clone 一致，不代表 clone 已是远端最新，也不代表 agent 已加载规则。

同步脚本保持标准库实现，兼容已有命令和标记。YAML 和 CommonMark 解析库仅为开发依赖，避免手写解析器误判合法文档。CI 使用临时目录，覆盖不同操作系统的文件行为；它不操作真实 Codex 主目录。

## 控制指令负担

描述只说明能力和触发边界；正文保留任务目标、关键判断与真实约束。长材料在有实际需要时拆成直接可达的引用。短 skill 可以只有一个正文，不为了整齐添加空目录或路由文件。

探索性工作给 agent 方法选择空间；容易损坏数据的重复操作使用脚本。是否写计划、开 PR、使用多个 agent、扩大测试范围，由任务需要决定。一次失败应先形成针对性修正，不自动升级成所有任务的永久规则。

## 依据与采用方式

| 来源 | 本仓库采用的原则 |
| --- | --- |
| [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills) | 区分发现、加载和执行；描述明确，资源按需读取 |
| [OpenAI：Rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | 缩短入口，避免每次任务都强制读取整套文档或固定流程 |
| [OpenAI：Testing skills with evals](https://developers.openai.com/blog/eval-skills) | 用任务结果和误触发样本评价行为，格式通过不等于有效 |
| [Anthropic：Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | 按任务的脆弱程度决定自由度；渐进披露；从实际表现迭代 |
| [Claude Code：Skills](https://code.claude.com/docs/en/skills) | 可移植内容与客户端扩展分开，按客户端说明安装 |
| [Agent Skills 开放规范](https://agentskills.io/specification) | `name`、`description` 等格式约束；每个包可独立使用 |
| [社区讨论：让 skill 同时服务人类](https://github.com/agentskills/agentskills/discussions/390) | 为人类提供单独入口；这项讨论是提案，不视为运行时标准 |

标准要求与写作建议应分别表达。例如，名称长度和必需字段属于格式约束；少于 500 行是写作建议，不能当作本仓库的自动失败条件。

## 兼容性与验证范围

通用 skill 内容遵循 Agent Skills 格式。Claude Code 的 `context`、动态命令注入等扩展并不保证能用于其他客户端；本仓库的全局规则安装器只处理 Codex。参考官方示例的设计，不等于已经在所有客户端完成运行验证。

检查分为三层：格式与引用、安装器行为、真实任务表现。CI 覆盖前两层；第三层在修改 skill 行为时选择代表任务检查。随新客户端、模型或实际失败重新审视规则，删去已无价值的限制。
