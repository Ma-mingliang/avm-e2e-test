# Agent Version Manager（AVM）完整总方案


---

<!-- 来源文件：README.md -->

# Agent Version Manager（AVM）完整方案文档包

本文件包用于指导构建一套面向 **Claude Code、Hermes、Codex** 的全局强制版本管理工具。第一版重点支持 Windows，默认安装目录为 `D:\AgentVersionManager\`；核心采用 Python，Windows 启动与安装入口采用 PowerShell。

## 文档索引与建议阅读顺序

1. `00_总纲与执行顺序.md`：项目目标、核心结论、实施顺序。
2. `01_需求规格与不可变规则.md`：全部已经确认的需求和不可违反规则。
3. `02_总体架构与目录结构.md`：全局工具、项目数据、适配层和安全边界。
4. `03_状态机与完整工作流.md`：初始化、任务、审批、PR、发布、中断与恢复。
5. `04_共享核心技术设计.md`：Python 核心模块、命令接口、锁、审批和 GitHub 操作。
6. `05_Claude_Code适配方案.md`：Claude Code Skill、Hooks、配置与包装启动器。
7. `06_Hermes适配方案.md`：Hermes Skill/Plugin、工具注册与项目规则。
8. `07_Codex适配方案.md`：Codex Skill、`AGENTS.md`、配置与包装启动器。
9. `08_对抗审查指令.md`：设计 Agent 与审查 Agent 的三轮内对抗审查流程。
10. `09_Claude_Code总控开发指令.md`：可直接交给 Claude Code 的总控指令。
11. `10_Claude_Code分阶段开发指令.md`：逐阶段开发、输出、门槛与回退要求。
12. `11_Codex独立功能测试指令.md`：开发目录回归 + 全新克隆环境端到端测试。
13. `12_测试矩阵与验收标准.md`：核心测试矩阵、发布门槛和缺陷等级。
14. `13_安装部署与使用手册.md`：Windows 安装、初始化、日常操作和故障恢复。
15. `14_严格审查结论与风险修正.md`：对原始构想的严厉审查、不可实现边界与修正。
16. `15_配置与报告模板.md`：配置、任务锁、版本报告、PR、Release 等模板。

## 最终架构结论

本方案不是单一 Skill，也不是单纯提示词。第一版采用：

- 一套全局 Python 核心；
- 一个 PowerShell 安装器与启动器；
- 三个 Agent 的独立适配层；
- 项目内可见的 `版本管理/` 数据目录；
- Claude Code/Hermes/Codex 各自的 Skill 或规则入口；
- 本地 Git Hooks；
- GitHub Ruleset、Pull Request、必需状态检查和 GitHub Actions；
- 用户中文审批、审批内容哈希绑定、审批变化失效；
- Git 标签 `v1、v2……` 与 GitHub Release；
- 文档本地版本 `doc-v1、doc-v2……`；
- 最新交接报告 + 按需回查历史的渐进式上下文机制。

## 关键安全声明

本工具能强制约束通过工具和正常 Git/GitHub 流程进行的操作，但无法对拥有管理员权限、能够删除 Hooks、使用 `--no-verify`、修改 GitHub Ruleset 或直接使用其他凭据的主体形成绝对安全隔离。因此，真正的强制力来自多层防线，而不是任何一个 Skill、Hook 或提示词。


---

<!-- 来源文件：00_总纲与执行顺序.md -->

# 00 总纲与执行顺序

## 1. 项目名称

建议正式名称：**Agent Version Manager（AVM，智能体版本管理器）**。

## 2. 项目目标

构建一套在 Windows 上全局安装、由 Claude Code、Hermes 和 Codex 共用核心逻辑但分别适配的版本管理工具。工具必须在真实项目修改前进行中文确认，在修改后形成可审查记录，并通过任务分支、Pull Request、Squash 合并、Git 标签和 GitHub Release 建立完整版本链。

其核心目标不是“自动提交”，而是实现以下闭环：

> 任务分类 → 中文确认 → 项目接手 → 版本预留 → 修改隔离 → 验证 → 中文审阅 → 用户批准 → PR 合并 → 标签 → Release → 交接报告更新 → 清理与归档。

## 3. 第一版范围

第一版必须实际完成：

- Windows 原生运行；
- Python 核心；
- PowerShell 安装、更新、启动入口；
- GitHub 作为唯一远程托管平台；
- GitHub CLI 优先认证，PAT 环境变量作为备用；
- Claude Code、Hermes、Codex 三套适配；
- 中文命令行与中文交互式菜单；
- Git、GitHub CLI、Git LFS、CI、Ruleset、Hooks、PR、标签、Release；
- 代码、配置、项目描述、版本信息的强制正式版本流程；
- Word、Excel、PPT、PDF、图片等文档的询问式流程；
- 修改前文档备份、SHA-256 清单和恢复校验；
- 中断接管、废弃任务、网络中断、发布失败恢复；
- 工具自身的版本、升级、快照和自动回滚。

第一版只规划但不要求实现：

- Linux、WSL、macOS 启动器；
- 图形界面；
- GitLab、Gitee、Bitbucket 适配；
- 多项目并发和同项目并行任务。

## 4. 核心设计判断

### 4.1 不能只做 Skill

Skill 适合表达任务流程和加载参考资料，但无法可靠完成版本号原子预留、远程锁、审批签名、Hook 校验、GitHub 发布事务和异常恢复。因此必须采用“共享核心程序 + Skill/Plugin 适配”的结构。

### 4.2 不能只依赖 Git Hooks

Git Hooks 是本地机制，可以被删除或用 `--no-verify` 绕过。正式分支必须同时配置 GitHub Ruleset，要求通过 PR、必需状态检查和受控合并。Hooks 负责本地早期拦截，Ruleset 和 CI 负责远程兜底。

### 4.3 必须区分项目版本与文档本地版本

- 正式项目版本：`v1、v2、v3……`，对应 PR、Squash 提交、标签和 Release。
- 未启用 GitHub 的文档任务：`doc-v1、doc-v2……`，只产生本地备份和记录，等待下一正式项目版本归档。

### 4.4 “全过程思考逻辑”应改为可审计决策记录

工具不得要求或伪造模型隐藏思维链。应记录：需求理解、关键假设、候选方案、选择理由、失败尝试、回退原因、验证证据和遗留问题。该内容可供审查和交接，但不是逐 token 内部推理。

## 5. 实施顺序

### 阶段 0：设计对抗审查

- 设计 Agent 输出完整设计；
- 审查 Agent 以反方身份检查；
- 最多三轮；
- 阻断级、严重级问题必须关闭；
- 三轮后仍未关闭则停止开发。

### 阶段 1：核心骨架

完成 CLI、配置加载、项目识别、中文输出、日志和异常模型。

### 阶段 2：Git 与状态机

完成仓库检测、分支、版本号、任务锁、Hook、差异快照和状态迁移。

### 阶段 3：GitHub 发布链

完成仓库创建、PR、草稿 PR、CI、Ruleset、Squash、标签、Release、资产审批。

### 阶段 4：文档备份

完成文档任务分类、修改前备份、哈希、清单、恢复和待归档队列。

### 阶段 5：Agent 适配

分别实现 Claude Code、Hermes、Codex 的 Skill/Plugin、规则文件和包装启动器。

### 阶段 6：安装、更新与自保护

完成 PowerShell 安装、配置备份、工具升级检查、本地快照和失败回滚。

### 阶段 7：系统测试

Claude Code 自测完成后，由 Codex 执行独立回归和全新克隆测试。

## 6. 官方能力依据

设计应以当前官方文档为准：

- Claude Code 支持用户级和项目级设置，以及生命周期 Hooks；
- Codex 支持全局与项目级 `AGENTS.md`、Skill 和 `config.toml`；
- Hermes 支持 Skill 和 Python Plugin；
- GitHub CLI 支持创建 PR、Squash 合并、创建标签对应的 Release；
- GitHub Ruleset 可要求 PR、状态检查和限制直接推送。

参考：

- https://docs.anthropic.com/en/docs/claude-code/settings
- https://docs.anthropic.com/en/docs/claude-code/hooks
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/skills
- https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md
- https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/work-with-skills.md
- https://cli.github.com/manual/gh_pr_create
- https://cli.github.com/manual/gh_pr_merge
- https://cli.github.com/manual/gh_release_create
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets


---

<!-- 来源文件：01_需求规格与不可变规则.md -->

# 01 需求规格与不可变规则

## 1. Agent 与实现方式

1. 支持 Claude Code、Hermes、Codex。
2. 三者分别实现适配入口，但共用同一套 Python 核心。
3. 所有正式版本管理动作必须通过共享核心执行。
4. 各 Agent 不得自行实现另一套版本号、任务锁、提交、PR、标签或 Release 逻辑。
5. 后续增加 Agent 时，只新增适配器，不复制核心。

## 2. 任务分类

### 2.1 强制正式版本管理

以下任务一旦确认开始，就必须走完整 GitHub 流程，否则不得修改：

- 真实代码修改；
- 配置文件修改；
- 项目描述、README、架构说明、版本说明等项目级文档修改；
- 版本管理规则和版本信息修改；
- CI/CD、部署、权限、依赖、数据库迁移等项目行为修改。

确认选项只能是：

- `确认开始`；
- `取消任务`。

不得提供“只在本地修改但不提交”的选项。

### 2.2 文档询问式管理

涉及 Word、Excel、PPT、PDF、图片、Draw.io、Visio 等资料文件时，必须先询问：

- 启用正式 GitHub 版本管理；或
- 仅执行本地文档版本管理。

如果用户选择本地文档版本管理：

- 允许修改；
- 必须保存修改前原文件；
- 必须生成 `doc-vN` 记录；
- 不创建正式 PR、标签或 Release；
- 记录和备份在下一次正式项目版本中统一归档。

### 2.3 特殊优先规则

任务分类不能只看“修改的是代码还是文档”，必须看任务最终目的。

例如：修改一个 Python 脚本，使其处理或修改 Word 文件，该任务属于“文档修改相关任务”，必须先询问用户是否启用正式版本管理，而不能因为修改了 `.py` 文件就自动进入强制正式流程。

### 2.4 Markdown 与纯文本

根据所在目录和用途判断：

- 项目说明、运行规范、版本记录、Agent 规则：强制正式版本管理；
- 独立资料、笔记、素材：文档询问式管理。

## 3. 中文规则

以下内容必须使用中文：

- 所有用户确认问题；
- Git 提交标题与正文；
- PR 标题与正文；
- Release 标题与说明；
- 版本报告、修改清单、验证报告、交接报告；
- 新增代码注释与配置注释；
- 错误说明和恢复建议；
- 安装和升级说明。

以下内容允许或必须保留原格式：

- 代码标识符；
- 命令；
- 文件路径；
- 第三方库和产品名称；
- 原始报错；
- 分支名、JSON/YAML 字段名等机器标识。

## 4. 版本规则

1. 正式版本为纯整数：`v1、v2、v3……`。
2. 文档本地版本为：`doc-v1、doc-v2……`。
3. 一次用户任务对应一个正式版本号。
4. 同一任务的返工、补充和用户审阅修改沿用原版本号。
5. 版本号一旦预留，不得复用。
6. 废弃 `v8` 后，下一个任务必须使用 `v9`。
7. 已有仓库接入时读取最大整数标签并递增。
8. 初始化无标签仓库时，基线发布为 `v1`。
9. 初始化已有 `v1…v7` 时，基线发布为 `v8`。
10. 正式版本一一对应：一个任务、一个 PR、一个 Squash 主分支提交、一个标签、一个 Release。

## 5. 分支与合并规则

1. 任务分支格式：`agent/vN-english-slug`。
2. 任务分支内部允许按实质阶段多次提交。
3. 禁止无意义提交，如“继续修改”“再次修复”。
4. 正式合并固定使用 Squash merge。
5. 用户批准后由工具自动调用 GitHub CLI 合并。
6. 标签和 Release 成功后才允许清理任务分支。
7. 标签或 Release 失败时，版本状态为“发布未完成”，禁止开始下一版本。
8. 成功任务分支在发布完成后自动删除本地和远程分支。
9. 废弃分支的清理必须先用中文展示并获得确认。

## 6. 并发与任务锁

1. 同一项目同一时间只允许一个活动修改任务。
2. 只读分析不占用修改锁。
3. 新 Agent 检测到活动锁、未合并任务分支或未关闭 PR 时，不得启动新修改任务。
4. 遗留任务必须生成《中断任务接管报告》并由用户选择继续、回滚、废弃或暂不处理。
5. 接管必须沿用原版本号、分支和 PR。
6. 不得按时间自动清理任务。

## 7. 接手规则

1. 新 Agent 首先读取根部最新《接手项目审查报告》；
2. 再读取该报告生成后的增量记录；
3. 无法理解任务或关键事实不确定时，按索引逐步回查更早版本；
4. 不允许一开始加载全部历史；
5. 不允许在历史设计意图不明时猜测并修改；
6. 完成任务后必须更新根部报告，并在当前版本目录保存完整报告副本。

## 8. 文档备份规则

1. Word、Excel、PPT、PDF、图片等在每次修改前保存原文件。
2. 备份目录与文件名都包含 `doc-vN`。
3. 示例：`版本管理/文档版本/doc-v3/修改前备份/论文_doc-v3_修改前.docx`。
4. 每个备份记录 SHA-256、原路径、大小、时间和 Agent。
5. 同时生成 `备份清单.md` 和 `manifest.json`。
6. 恢复前自动验证哈希。
7. 是否使用 Git LFS 由初始化扫描后提出中文建议，用户确认后配置。

## 9. 审批规则

1. 修改完成后先生成差异、报告、提交说明、PR 说明和 Release 说明。
2. 用户可修改上述内容。
3. 用户明确批准后，不再进行第三次确认，按用户修改后的内容执行。
4. 批准记录绑定文件清单、文件哈希、基准提交、配置哈希和说明文本哈希。
5. 批准后任何已批准内容发生变化，批准立即失效。
6. 失效后必须重新生成材料并再次审批。
7. 所有确认界面必须中文。

## 10. 验证与 CI

1. 项目配置中保存测试、构建、格式检查、文档校验命令。
2. 本地和 CI 尽量使用同一套命令。
3. 本地失败只能创建草稿 PR。
4. CI 全部通过后才能转正式 PR。
5. 测试失败时保留原版本、分支和草稿 PR。
6. 下一 Agent 经用户批准后可接管修复。
7. 没有 CI 的项目，初始化时生成基础 CI；写入前中文展示并确认。

## 11. 安全与敏感信息

1. 初始化和提交前必须扫描密钥、Token、密码、私钥、`.env`、Cookie、凭据、个人数据、大文件、模型权重、缓存和日志。
2. 命中高风险项时立即阻止提交和发布。
3. 由用户选择忽略、脱敏、加入 `.gitignore`、使用 Git LFS 或取消。
4. 不得把 PAT、API Key、凭据写入项目、日志或报告。
5. GitHub 优先使用 `gh auth`，PAT 只从环境变量读取。
6. 新建远程仓库默认私有。

## 12. 修改范围扩大规则

必须重新确认的情况：

- 任何高风险文件被新增或修改；
- 普通文件新增超过 5 个；
- 实际修改总数超过预计数量 50%；
- 扩展到原计划外的新一级目录；
- 修改部署、权限、认证、数据库迁移、CI/CD、依赖锁、Git Hooks 或生产配置。

自动生成的版本记录和规定内报告不计入数量阈值。

## 13. 清理与保留

1. 正式版本记录永久保留。
2. 失败、废弃和临时内容只能在中文列出后由用户批准清理。
3. Agent 全局配置备份永久保留。
4. 工具升级前创建本地完整快照；失败自动回滚。
5. Release 资产必须先中文列出，由用户确认后上传。


---

<!-- 来源文件：02_总体架构与目录结构.md -->

# 02 总体架构与目录结构

## 1. 总体架构

```text
Claude Code Adapter ─┐
Hermes Adapter ──────┼──> AVM Python Core ──> Git / GitHub CLI / Git LFS
Codex Adapter ───────┘          │
                                ├── 项目状态机
                                ├── 版本与任务锁
                                ├── 中文审批
                                ├── 文档备份
                                ├── 报告生成
                                ├── 本地 Hooks
                                ├── CI / Ruleset 管理
                                └── 升级与回滚
```

## 2. 全局安装目录

Windows 默认：

```text
D:\AgentVersionManager\
├─ avm.ps1
├─ install.ps1
├─ update.ps1
├─ rollback.ps1
├─ pyproject.toml
├─ src\avm\
│  ├─ cli.py
│  ├─ core\
│  ├─ git\
│  ├─ github\
│  ├─ approval\
│  ├─ backup\
│  ├─ reports\
│  ├─ adapters\
│  ├─ security\
│  └─ update\
├─ hooks\
├─ templates\
├─ schemas\
├─ tests\
├─ config-backups\
├─ snapshots\
└─ logs\
```

如果设备没有 D 盘，安装器推荐：

```text
%USERPROFILE%\.agent-version-manager\
```

安装路径允许用户在中文界面中修改。

## 3. 每个项目的目录

```text
项目根目录\
├─ 版本管理\
│  ├─ 配置.yaml
│  ├─ 版本索引.md
│  ├─ 版本索引.json
│  ├─ 当前任务.json
│  ├─ 最新接手项目审查报告.md
│  ├─ 正式版本\
│  │  ├─ v1\
│  │  │  ├─ 更新说明.md
│  │  │  ├─ 修改文件清单.md
│  │  │  ├─ 验证报告.md
│  │  │  ├─ 决策与执行记录.md
│  │  │  ├─ 提交与发布说明.md
│  │  │  ├─ 接手项目审查报告.md
│  │  │  ├─ approval.json
│  │  │  └─ metadata.json
│  │  └─ v2\
│  ├─ 文档版本\
│  │  ├─ doc-v1\
│  │  │  ├─ 修改前备份\
│  │  │  ├─ 文档修改说明.md
│  │  │  ├─ 备份清单.md
│  │  │  ├─ manifest.json
│  │  │  └─ metadata.json
│  │  └─ doc-v2\
│  ├─ 废弃版本\
│  ├─ 中断任务\
│  ├─ 待归档文档记录\
│  └─ 临时\
├─ .claude\
│  └─ settings.json
├─ .codex\
│  └─ config.toml
├─ CLAUDE.md
├─ AGENTS.md
├─ .github\
│  ├─ workflows\
│  │  └─ avm-policy.yml
│  └─ pull_request_template.md
└─ 项目文件……
```

## 4. 机器数据与中文报告

- JSON/YAML/TOML 字段名使用 ASCII 英文。
- 字段值、报告正文和确认内容使用中文。
- `版本管理/` 使用中文名称，便于人工查看。
- 分支名使用 ASCII，避免终端和跨平台兼容问题。

## 5. 核心适配接口

每个 Agent 适配器只需要实现：

```python
class AgentAdapter(Protocol):
    name: str
    def detect(self) -> bool: ...
    def install_global_rules(self) -> None: ...
    def install_project_rules(self, project_root: Path) -> None: ...
    def render_confirmation(self, payload: dict) -> str: ...
    def launch_wrapped(self, project_root: Path, args: list[str]) -> int: ...
```

适配器不得直接实现：

- 版本号递增；
- Git 提交；
- PR 创建和合并；
- 标签和 Release；
- 审批签名；
- 文档备份；
- 任务锁。

## 6. 多层强制结构

### 第一层：Agent 规则

- Claude Code：`CLAUDE.md`、项目设置、Hooks、Skill。
- Hermes：Skill/Plugin、项目规则和包装启动器。
- Codex：全局/项目 `AGENTS.md`、Skill、`config.toml`、包装启动器。

### 第二层：统一工具

任何写入任务先执行 `avm preflight`，任何正式发布执行 `avm publish`。

### 第三层：本地 Git Hooks

- `pre-commit`：检查任务锁、分支、审批状态、版本记录和敏感信息。
- `commit-msg`：检查中文提交格式和版本号。
- `pre-push`：阻止直接推送正式分支、未审批标签和不完整版本。

### 第四层：GitHub 远程控制

- Ruleset 要求通过 PR；
- 要求状态检查；
- 限制直接推送；
- 固定 Squash merge；
- CI 检查 AVM 元数据和版本一致性。

## 7. 安全边界

必须明确：

- 本地 Hooks 可被 `--no-verify` 绕过；
- 有管理员权限的人可以修改 Ruleset；
- 持有高权限 GitHub 凭据的进程可以绕开工具；
- Skill 和提示词不能形成操作系统级强制隔离。

因此 AVM 的目标是“对正常 Agent 工作流提供强约束和可审计防线”，不是对恶意管理员或完全失控进程提供不可突破的安全沙箱。

## 8. 新空仓库的引导例外

新建空 GitHub 仓库时不存在默认分支，无法先创建 PR。必须设计一次性“引导提交例外”：

1. 用户用中文批准初始化；
2. 工具创建私有仓库；
3. 创建受控的初始提交并推送默认分支；
4. 立即安装 Ruleset、CI 和 Hooks；
5. 创建 `v1` 标签和 Release；
6. 在 `v1` 报告中明确记录该引导例外。

除空仓库初始化外，不允许直接推送正式分支。


---

<!-- 来源文件：03_状态机与完整工作流.md -->

# 03 状态机与完整工作流

## 1. 正式任务状态机

```text
IDLE
  ↓
PREFLIGHT
  ↓
WAIT_START_APPROVAL
  ↓
RESERVED
  ↓
LOCKED
  ↓
BRANCH_READY
  ↓
MODIFYING
  ↓
VALIDATING
  ├─失败→ DRAFT_PR / FIXING
  └─通过→ REVIEW_MATERIAL_READY
                 ↓
          WAIT_FINAL_APPROVAL
                 ↓
              PR_READY
                 ↓
             MERGING
                 ↓
             TAGGING
                 ↓
            RELEASING
                 ↓
          HANDOFF_UPDATING
                 ↓
             CLEANING
                 ↓
             COMPLETE
```

异常状态：

```text
INTERRUPTED
ABANDONED
PUBLISH_INCOMPLETE
AUTH_BLOCKED
NETWORK_BLOCKED
SECURITY_BLOCKED
APPROVAL_INVALIDATED
```

## 2. 修改前预检

执行：

```powershell
avm preflight --project <路径> --agent claude-code --task "任务描述"
```

预检必须完成：

1. 定位 Git 根目录；
2. 读取项目配置；
3. 检查 Git、`gh`、LFS、认证和网络；
4. 读取最新交接报告和增量；
5. 检查活动任务锁、远程锁分支、未关闭 PR；
6. 检查未提交修改；
7. 任务分类；
8. 估计修改文件范围；
9. 扫描高风险文件；
10. 计算下一个永不复用版本号；
11. 生成中文确认界面。

## 3. 强制任务确认界面

```text
【项目修改确认】

项目：<项目名称>
正式分支：<main/master>
当前正式版本：v7
本次预留版本：v8
任务分支：agent/v8-task-slug
执行 Agent：Claude Code

任务类型：真实代码/配置/项目说明修改
预计修改范围：
- src/...
- config/...
- tests/...

系统将执行：
1. 预留 v8，且预留后不得复用；
2. 获取项目修改锁；
3. 创建独立任务分支；
4. 修改、测试并生成中文版本记录；
5. 创建 Pull Request；
6. 经你审阅批准后 Squash 合并；
7. 创建 v8 标签和 GitHub Release；
8. 更新接手项目审查报告。

请选择：
[确认开始]
[取消任务]
```

## 4. 文档任务确认界面

```text
【文档修改方式确认】

本次任务涉及 Word/Excel/PPT/PDF/图片或相关处理代码。

请选择：
[启用完整 GitHub 版本管理]
[仅执行本地文档版本管理]
[取消任务]
```

选择本地模式后：

- 分配 `doc-vN`；
- 修改前备份；
- 生成清单和记录；
- 不推送；
- 加入“待归档文档记录”。

## 5. 任务锁

### 5.1 本地锁

`版本管理/当前任务.json` 记录：

- task_id；
- version；
- agent；
- branch；
- base_commit；
- start_time；
- status；
- expected_files；
- remote_lock_ref。

### 5.2 远程原子锁

建议使用专用远程分支 `avm/system-lock`：

- 获取锁：以“仅创建、不覆盖”方式推送；
- 分支已存在则获取失败；
- 锁分支提交中只保存锁元数据；
- 正常完成或经用户批准废弃后删除；
- 不进入正式分支历史。

该方式比“先查询再创建 GitHub Issue”更接近原子互斥。

## 6. 修改与范围扩大

Agent 修改前记录预计文件范围。执行中出现以下情况立即暂停：

- 高风险文件；
- 新增普通文件超过 5 个；
- 实际文件数超过预计 50%；
- 新一级目录；
- 生产、权限、认证、CI、部署、迁移、锁文件、Hook。

暂停时必须生成中文差异说明并重新请求确认。

## 7. 阶段提交

复杂任务可进行阶段提交：

- 基线与项目审查；
- 核心修改；
- 测试与修复；
- 版本报告；
- 用户审阅调整。

每次阶段提交前仍受 Hook 约束，但尚不需要最终发布审批。阶段提交只存在任务分支，最终 Squash。

## 8. 验证失败

1. 保存失败命令、退出码、stdout/stderr 摘要；
2. 生成《验证失败报告》；
3. 允许创建草稿 PR；
4. 禁止正式合并、标签和 Release；
5. 保留版本号、分支、锁和 PR；
6. 当前 Agent 可继续修复；
7. 下一 Agent 接管必须经用户批准。

## 9. 最终审批

工具生成：

- 更新说明；
- 修改文件清单；
- 验证报告；
- 决策与执行记录；
- 提交标题与正文；
- PR 标题与正文；
- Release 标题与正文；
- 可选 Release 资产列表。

用户可以编辑。用户选择“批准执行”后，工具生成审批记录并执行，不再增加第三次确认。

## 10. 审批失效

审批记录包含规范化清单哈希：

```text
approval_hash = SHA256(
  base_commit +
  sorted(file_path + file_sha256) +
  commit_message_hash +
  pr_body_hash +
  release_body_hash +
  config_hash
)
```

审批后重新计算不一致，状态转为 `APPROVAL_INVALIDATED`，必须重新审批。

建议使用全局工具私有密钥对审批记录做 HMAC，密钥保存在 Windows Credential Manager 或受保护的全局配置区，不写入项目。

## 11. 合并与发布事务

发布顺序固定：

1. 确认 CI 成功；
2. `gh pr merge --squash`；
3. 读取实际 Squash 提交哈希；
4. 创建注释标签 `vN` 指向该提交；
5. 推送标签；
6. 创建 GitHub Release；
7. 用户确认后上传资产；
8. 更新报告和交接文档；
9. 完成审计提交或确保报告已包含于 Squash 提交；
10. 删除任务分支和远程锁。

注意：为了让“最终接手报告”进入同一 Squash 提交，报告必须在 PR 合并前生成。合并后只能补写不可变的远程对象信息。解决方式是：PR 中先写入预期字段，合并后把实际提交哈希、Release URL 等写入 GitHub Release 元数据和全局状态；下一版本再把最终远程引用同步回仓库，或在合并前通过 GitHub API 预测不了的字段保留占位符。第一版建议将“仓库内报告”保存 PR、版本和预期发布信息，将实际远程 URL 存入 Release 与 `版本索引.json` 的本地后置记录，避免为了补哈希再制造额外主分支提交。

## 12. 发布失败

若 PR 已合并而标签或 Release 失败：

- 状态为 `PUBLISH_INCOMPLETE`；
- 原版本号继续占用；
- 禁止新任务；
- 不删除任务分支和锁；
- 重试时必须确认主分支提交未变化；
- 成功后恢复正常闭环。

## 13. 中断接管

新 Agent 只读检查并生成：

- 当前锁；
- 分支；
- 未提交修改；
- 未推送提交；
- PR 状态；
- 测试状态；
- 文档备份；
- 已生成报告；
- 风险。

用户选择继续、回滚、废弃或暂不处理。未经选择，不得变更状态。

## 14. 废弃版本

- 版本号永久作废；
- 关闭草稿 PR；
- 保留 PR 作为远程证据；
- 本地保存废弃原因和状态；
- 不创建正式 `vN` 标签和 Release；
- 废弃记录在下一个正式版本中纳入主分支；
- 清理分支前再次中文确认。


---

<!-- 来源文件：04_共享核心技术设计.md -->

# 04 共享核心技术设计

## 1. 技术栈

- Python 3.11+；
- Typer 或 Click：CLI；
- Pydantic：配置和状态模型；
- PyYAML 或 ruamel.yaml：项目配置；
- Rich：中文终端界面；
- subprocess：调用 Git、`gh`、Git LFS；
- keyring/Windows Credential Manager：审批签名密钥；
- pytest：测试；
- packaging：版本比较；
- platformdirs：全局数据目录；
- filelock：单进程本地锁；
- hashlib：SHA-256；
- Jinja2：报告模板。

尽量减少依赖，所有外部命令必须以参数数组调用，不得拼接未转义 shell 字符串。

## 2. 核心模块

```text
src/avm/
├─ cli.py
├─ models.py
├─ config.py
├─ project.py
├─ classifier.py
├─ state_machine.py
├─ versioning.py
├─ locking.py
├─ approval.py
├─ reports.py
├─ backup.py
├─ validation.py
├─ security_scan.py
├─ git_ops.py
├─ github_ops.py
├─ hooks.py
├─ updater.py
├─ recovery.py
└─ adapters/
```

## 3. 命令设计

```text
avm doctor
avm install
avm update-check
avm update
avm rollback
avm init-project
avm status
avm preflight
avm start
avm checkpoint
avm validate
avm prepare-review
avm approve
avm create-pr
avm merge
avm publish
avm resume
avm abandon
avm recover
avm document-start
avm document-complete
avm archive-pending-docs
avm backup-list
avm backup-restore
avm config-backup-list
avm config-restore
avm launch claude
avm launch hermes
avm launch codex
```

所有破坏性或配置修改命令必须交互式中文确认，且支持 `--json` 供 Agent 读取机器结果。

## 4. 配置模型

全局配置只保存工具级设置，项目配置保存项目差异。安全和审计项不可被项目覆盖。

示例见 `15_配置与报告模板.md`。

## 5. 版本号算法

输入来源：

- Git 标签 `^v[1-9][0-9]*$`；
- `版本索引.json` 中正式、废弃、预留版本；
- 活动锁；
- 远程任务分支；
- 开放和关闭 PR 中的 AVM 元数据。

算法：

```python
next_version = max(all_known_integer_versions, default=0) + 1
```

必须拒绝：

- 非整数标签误当正式版本；
- 本地与远程索引冲突；
- 同一版本对应多个 PR；
- 标签指向非正式分支提交。

## 6. 任务分类器

采用规则优先而非纯 LLM：

1. 用户任务最终目标；
2. 预计写入文件类型；
3. 目录语义；
4. 高风险规则；
5. Agent 判断补充。

分类结果：

```text
MANDATORY_PROJECT_VERSION
OPTIONAL_DOCUMENT_VERSION
READ_ONLY
BLOCKED_UNCLEAR
```

存在歧义时必须输出中文问题，不得默认进入较弱流程。

## 7. Git 操作原则

- 所有操作前记录当前 HEAD、分支、工作区状态；
- 使用 `git status --porcelain=v2`；
- 使用 `git diff --binary` 生成审计摘要，但不把大二进制 diff 塞入报告；
- 禁止 `git reset --hard`、`git clean -fd` 等破坏命令，除非用户明确批准；
- 回滚优先使用新提交或恢复指定文件；
- 标签使用 annotated tag；
- 推送使用显式远程和 refspec；
- 正式分支禁止工具外直推。

## 8. GitHub 操作

优先通过 `gh`：

- `gh auth status`；
- `gh repo create --private`；
- `gh pr create --draft`；
- `gh pr ready`；
- `gh pr checks`；
- `gh pr merge --squash --delete-branch`；
- `gh release create`；
- `gh release upload`。

任何命令失败都要保存退出码和最小必要输出，认证信息必须脱敏。

## 9. Ruleset 与 CI

初始化时生成建议：

- 正式分支必须通过 PR；
- 禁止删除正式分支；
- 必需状态检查；
- 需要分支为最新；
- 固定允许 Squash merge；
- 阻止直接推送；
- 可选限制提交元数据和分支名。

Ruleset 的可用能力与 GitHub 计划有关，工具必须先检测账户和仓库支持情况。若私有仓库当前计划不支持目标规则，必须中文说明降级，不得宣称已经获得同等强制力。

## 10. 审批系统

审批分为：

- 修改前开始审批；
- 修改范围扩大审批；
- 最终发布审批；
- Release 资产审批；
- 中断接管审批；
- 清理审批；
- 工具升级审批。

审批记录必须包含：

- approval_id；
- approval_type；
- user_decision；
- version；
- task_id；
- manifest_hash；
- issued_at；
- expires_on_change；
- HMAC signature。

## 11. 文档备份

备份流程：

1. 路径规范化；
2. 检查源文件存在；
3. 计算源 SHA-256；
4. 复制到临时文件；
5. fsync/关闭；
6. 重新计算备份 SHA-256；
7. 验证相同；
8. 原子重命名到目标；
9. 写清单；
10. 完成后才允许文档修改。

文件名冲突时加入短哈希，不覆盖已有备份。

## 12. 报告生成

所有报告由结构化数据渲染，避免 Agent 随意漏字段。Agent 负责补充中文解释，核心工具负责保证必填项。

## 13. 日志与隐私

- 日志默认位于全局工具目录，不提交项目；
- 日志不得记录 Token、完整环境变量、私钥、Cookie；
- 命令输出先脱敏；
- 日志分为 INFO、AUDIT、ERROR；
- 项目报告只记录可审计事实。

## 14. 更新机制

- 检测远程 Release；
- 中文展示当前版本、目标版本、更新内容、兼容性和备份位置；
- 用户确认后升级；
- 升级前完整快照；
- 执行迁移 dry-run；
- 失败自动回滚；
- 工具自身用独立 Git 仓库、标签和 Release。


---

<!-- 来源文件：05_Claude_Code适配方案.md -->

# 05 Claude Code 适配方案

## 1. 适配目标

Claude Code 适配由四部分组成：

1. 全局 Skill；
2. 项目 `CLAUDE.md`；
3. Claude Code Hooks；
4. `avm launch claude` 包装启动器。

Claude Code 官方支持用户级和项目级设置，以及生命周期 Hooks，因此可用 Hooks 在写文件或执行 Git 命令前后调用 AVM 检查。

## 2. 全局配置

安装器检测并备份：

```text
%USERPROFILE%\.claude\settings.json
```

修改前必须用中文展示：

- 文件路径；
- 原值摘要；
- 新值摘要；
- 备份位置；
- 恢复命令。

## 3. 项目文件

项目根目录写入：

```text
CLAUDE.md
.claude/settings.json
```

`CLAUDE.md` 必须简短，包含：

- 任何写入前运行 `avm preflight`；
- 强制任务不得绕过；
- 文档任务必须询问；
- 所有确认与报告中文；
- 不得直接 commit/push/tag/release；
- 必须读取最新交接报告；
- 理解不足时按索引回查；
- 修改完成后调用 `avm prepare-review`。

## 4. Skill 结构

```text
~/.claude/skills/avm-version-control/
├─ SKILL.md
├─ references/
│  ├─ workflow.md
│  ├─ task-classification.md
│  └─ recovery.md
└─ scripts/
   └─ avm.ps1
```

Skill 只负责指导 Claude Code 何时调用工具，不复制核心实现。

## 5. Hooks

应评估当前 Claude Code Hook 事件并选择最接近以下语义的事件：

- 工具调用前：拦截写文件、Shell Git 命令；
- 工具调用后：记录新增修改；
- 会话开始：检查项目状态和遗留锁；
- 会话结束：提示未完成任务和生成交接材料。

Hook 脚本只调用：

```powershell
D:\AgentVersionManager\avm.ps1 hook claude --event <event>
```

不要把业务规则复制到 Hook 文件。

## 6. 包装启动器

```powershell
avm launch claude --project D:\project
```

行为：

1. 检查项目是否初始化；
2. 检查活动任务；
3. 检查 Claude 配置；
4. 注入 AVM 环境变量；
5. 启动 Claude Code；
6. 记录 Agent 身份和会话 ID。

## 7. 失败降级

如果 Claude Code Hook API 或配置格式发生变化：

- 不得静默失效；
- `avm doctor` 必须报告；
- 包装启动器仍执行前置检查；
- Git Hooks 和 GitHub CI 继续兜底；
- 更新适配器前必须备份全局配置。


---

<!-- 来源文件：06_Hermes适配方案.md -->

# 06 Hermes 适配方案

## 1. 适配选择

Hermes 同时支持 Skills 和 Python Plugins。AVM 应采用：

- Skill：描述工作流、触发条件、中文交互规范；
- Plugin：注册结构化 AVM 工具调用；
- 包装启动器：在进入项目时执行状态检查。

不建议只写 Skill，因为任务锁、审批和发布必须由确定性代码执行。

## 2. Plugin 结构

```text
hermes-avm-plugin/
├─ pyproject.toml
├─ src/hermes_avm_plugin/
│  ├─ __init__.py
│  ├─ plugin.py
│  └─ tools.py
└─ skills/
   └─ avm-version-control/
      ├─ SKILL.md
      └─ references/
```

Plugin 注册的工具建议：

```text
avm_status
avm_preflight
avm_start
avm_validate
avm_prepare_review
avm_resume
avm_abandon
avm_document_start
avm_document_complete
```

涉及最终批准、合并、Release 和清理的工具必须要求交互式用户决策，不能由 Hermes 自主默认为“是”。

## 3. Hermes 项目接手

Hermes 启动任务时：

1. 读取最新交接报告；
2. 读取增量；
3. 需要时调用 Skill 中的历史回查规则；
4. 不把全部历史一次性加载；
5. 将回查版本写入执行记录。

这利用 Skill 的按需加载特性，减少每次请求的上下文占用。

## 4. 配置修改

安装器检测 Hermes 实际安装和配置目录，不能假定所有版本路径一致。任何配置修改必须：

- 先完整备份；
- 中文展示差异；
- 用户确认；
- 执行后运行 Hermes 自检或等价健康检查；
- 失败自动恢复原配置。

## 5. 包装启动器

```powershell
avm launch hermes --project D:\project
```

包装器可以设置项目路径和 AVM 环境变量，然后调用 Hermes CLI 或已安装入口。实际命令必须在安装阶段探测，而不是写死。

## 6. 安全要求

- Hermes 的 terminal/file tools 不能直接承担正式 Git 发布；
- 即便 Hermes 可以调用 shell，也必须调用 AVM CLI；
- Plugin 返回结构化状态，不返回密钥；
- 所有工具结果中文解释，机器字段 ASCII。


---

<!-- 来源文件：07_Codex适配方案.md -->

# 07 Codex 适配方案

## 1. 适配目标

Codex 官方支持：

- 全局和项目级 `AGENTS.md`；
- 全局和项目级 `config.toml`；
- Agent Skills；
- CLI 和桌面应用。

AVM 适配采用：

1. 全局 Skill；
2. 全局 `AGENTS.md` 基础规则；
3. 项目 `AGENTS.md` 详细规则；
4. 项目 `.codex/config.toml`；
5. `avm launch codex` 包装启动器。

## 2. Skill 结构

```text
%USERPROFILE%\.codex\skills\avm-version-control\
├─ SKILL.md
├─ references\
└─ scripts\
```

Skill 内容应精简，使用 progressive disclosure：元数据只描述触发条件，完整流程放 references。

## 3. AGENTS.md 规则

全局文件只写不可变规则：

- 写入前调用 AVM；
- 不直接 commit/push/tag/release；
- 所有确认中文；
- 任何审批后变更使批准失效。

项目 `AGENTS.md` 写：

- 项目测试命令；
- 正式分支；
- 文件分类；
- 接手报告位置；
- 版本记录位置；
- 项目特殊限制。

## 4. 配置

Codex 用户配置通常位于：

```text
%USERPROFILE%\.codex\config.toml
```

项目配置：

```text
项目根目录\.codex\config.toml
```

安装器必须先读取官方当前配置格式，展示差异并备份。项目必须被 Codex 识别为受信任后，项目级配置才可靠生效，因此 `avm doctor` 应检查信任状态或给出明确提示。

## 5. 包装启动器

```powershell
avm launch codex --project D:\project
```

功能：

- 预检；
- 状态锁检查；
- 规则文件一致性检查；
- 启动 Codex CLI 或 App 对应入口；
- 保存 Agent 身份和测试会话标识。

## 6. Codex 在本项目中的双重角色

- 日常使用：作为三 Agent 之一，遵守 AVM。
- 工具开发验收：作为独立测试者，不接受 Claude Code 的自测结论，按 `11_Codex独立功能测试指令.md` 测试。


---

<!-- 来源文件：08_对抗审查指令.md -->

# 08 对抗审查指令

## 1. 使用方式

优先由不同 Agent 执行：

- 设计 Agent：Claude Code 或 Hermes；
- 审查 Agent：Codex 或另一独立 Agent。

无法使用不同 Agent 时，可由同一 Agent 分角色执行，但必须分别输出文档，不得把设计与审查混写。

## 2. 设计 Agent 指令

```text
你是本项目的设计 Agent。请完整阅读需求规格、总体架构、状态机和技术设计。你的任务不是直接编码，而是产出可实现、可测试、可恢复的最终设计。

必须：
1. 对每条需求建立可追踪编号；
2. 给出实现模块、数据模型、状态机和命令接口；
3. 区分确定性程序约束与 Agent 提示词约束；
4. 明确 Git Hooks、GitHub Ruleset、CI 和管理员权限的安全边界；
5. 推演新空仓库、已有仓库、未提交修改、网络中断、认证失效、PR 合并后 Release 失败、审批后文件变化、文档备份损坏、任务中断和废弃版本；
6. 不得以“后续再考虑”跳过核心能力；
7. 输出《设计方案_vN.md》和《需求追踪矩阵_vN.md》。

禁止写代码，直到审查门槛通过。
```

## 3. 审查 Agent 指令

```text
你是独立审查 Agent。你的立场是最严厉的反方审计者，而不是帮助设计者证明方案正确。

请逐条攻击以下方面：
1. 需求是否存在冲突、遗漏或不可实现表述；
2. 是否把提示词、Skill 或本地 Hook 夸大为不可绕过安全机制；
3. 版本号是否可能重复、断裂或复用；
4. 远程任务锁是否真正能阻止竞争；
5. PR、Squash、标签、Release 是否满足事务一致性；
6. 报告在合并前后生成是否造成额外提交或信息不完整；
7. 文档本地版本何时进入 Git，是否可能永久滞留；
8. 新空仓库在没有默认分支时如何建立 PR 规则；
9. 用户审批是否绑定实际提交内容；
10. Agent 是否能通过 shell、--no-verify、改配置或换凭据绕过；
11. 私有仓库的 GitHub 计划是否支持预期 Ruleset；
12. CI 是否能被跳过；
13. 配置备份、升级回滚和恢复是否可验证；
14. Windows 路径、编码、中文文件名、PowerShell 引号和长路径是否处理；
15. 是否存在删除用户文件、泄露密钥或错误回滚风险；
16. 测试是否足以证明功能，而不是只证明快乐路径。

每个问题标记：阻断级、严重级、一般级、建议级。
对每项给出：证据、复现场景、影响、必须修改内容、验证方式。
输出《独立审查报告_第N轮.md》。不得直接覆盖设计方案。
```

## 4. 修订规则

设计 Agent 必须逐条响应：

```text
问题编号 | 是否接受 | 修订位置 | 修订内容 | 验证方法 | 剩余风险
```

不得用“已优化”“已处理”代替具体修订。

## 5. 强制替代方案

若设计 Agent 两次修订仍未解决同一严重问题，审查 Agent可提交《强制替代方案.md》，包括：

- 原方案失败原因；
- 替代架构；
- 迁移影响；
- 新风险；
- 最小验证原型。

审查 Agent仍不得直接修改正式代码。

## 6. 退出条件

- 最多三轮；
- 阻断级和严重级必须全部关闭；
- 一般级可进入后续改进清单；
- 三轮后仍有阻断级或严重级，停止开发并向用户报告。


---

<!-- 来源文件：09_Claude_Code总控开发指令.md -->

# 09 Claude Code 总控开发指令

以下内容可直接交给 Claude Code。

```text
你将开发 Agent Version Manager（AVM）第一版。工作目录由用户指定；Windows 默认安装目标为 D:\AgentVersionManager\。

你必须先阅读本方案文档包中的全部设计文档，但不得把全部内容一次性塞进上下文。先读 README、00、01、02、03，再按当前阶段按需读取其他文档。

绝对规则：
1. 任何代码前先完成双角色对抗审查，最多三轮；阻断级和严重级全部关闭后才可编码。
2. 所有面向用户的确认、报告、提交、PR 和 Release 内容使用中文。
3. 代码标识符、机器字段和分支名使用 ASCII。
4. 不得声称 Git Hooks 或 Skill 是不可绕过的安全机制。
5. 不得执行删除文件、修改 Agent 全局配置、修改 Git 全局配置或安装软件，除非先用中文说明影响并获得用户确认。
6. 每个阶段完成后生成阶段报告、测试证据和未解决问题。
7. 不得跳过失败测试，不得用空测试或 mock 全部外部行为来宣称端到端通过。
8. 使用 Python 3.11+，PowerShell 作为 Windows 安装与启动入口。
9. 第一版实际支持 Windows/GitHub；其他操作系统和托管平台只保留接口与文档。
10. 任何敏感信息不得写入代码、测试固定数据、日志或仓库。

开发策略：
- 先建立需求追踪矩阵；
- 使用状态机驱动，而不是散乱脚本；
- 所有 Git/GitHub 调用封装；
- 所有状态文件使用 schema 版本；
- 文件写入使用临时文件 + 原子替换；
- 破坏性操作默认禁止；
- 外部命令参数数组化；
- 每个异常路径必须有恢复测试。

必须按《10_Claude_Code分阶段开发指令.md》执行。每个阶段只有在该阶段验收通过后才能进入下一阶段。

最终输出：
1. 可安装源码；
2. Windows 安装器和启动器；
3. 三 Agent 适配；
4. 单元、集成和端到端测试；
5. GitHub Actions；
6. 示例项目；
7. 中文使用手册；
8. 版本和 Release；
9. 提交给 Codex 的独立测试包；
10. 已知限制列表。
```


---

<!-- 来源文件：10_Claude_Code分阶段开发指令.md -->

# 10 Claude Code 分阶段开发指令

## 阶段 0：环境与设计审计

任务：

- 检查 Python、PowerShell、Git、gh、Git LFS；
- 不修改全局配置；
- 建立需求追踪矩阵；
- 执行对抗审查；
- 输出最终设计冻结版。

门槛：无阻断级或严重级问题。

## 阶段 1：项目骨架与数据模型

实现：

- Python 包；
- CLI；
- 中文输出；
- 配置 schema；
- 状态枚举；
- 审计日志；
- 路径和编码处理。

测试：

- Windows 路径；
- 中文目录；
- 空格；
- 长路径；
- 非 Git 目录；
- 配置迁移。

## 阶段 2：Git 核心

实现：

- 仓库识别；
- 状态读取；
- 版本号；
- 分支；
- 阶段提交；
- 标签；
- Hook 安装和校验；
- 未提交修改报告。

禁止：在测试中操作真实用户仓库。

## 阶段 3：任务状态机与锁

实现：

- 本地锁；
- 远程 `avm/system-lock`；
- 版本预留；
- 中断、恢复、废弃；
- 状态迁移合法性。

测试竞争、锁残留和错误释放。

## 阶段 4：审批与范围控制

实现：

- 中文确认；
- 预计文件范围；
- 高风险规则；
- 5 个/50% 阈值；
- 审批清单哈希；
- HMAC；
- 变化失效。

必须证明批准后修改任何文件都会被阻止发布。

## 阶段 5：文档备份

实现：

- `doc-vN`；
- 修改前复制；
- SHA-256；
- manifest；
- 恢复校验；
- 待归档队列；
- LFS 建议。

测试二进制损坏、同名文件、超大文件、权限失败和磁盘空间不足。

## 阶段 6：GitHub 工作流

实现：

- gh 认证检查；
- 私有仓库创建；
- 草稿/正式 PR；
- CI；
- Squash；
- 标签；
- Release；
- 资产询问；
- 发布未完成恢复。

使用专用测试仓库，不得污染真实项目。

## 阶段 7：初始化流程

实现：

- 新项目；
- 已有项目；
- 最大标签递增；
- 未提交修改选择；
- 敏感扫描；
- 默认分支确认；
- CI 和 Ruleset 建议；
- 空仓库引导例外；
- 基线版本发布。

## 阶段 8：报告与交接

实现所有模板和索引。验证最新报告不无限增长，并能按需回查历史。

## 阶段 9：三 Agent 适配

分别实现：

- Claude Code Skill/Hooks/包装器；
- Hermes Skill/Plugin/包装器；
- Codex Skill/AGENTS/config/包装器。

所有全局配置修改先备份并中文确认。

## 阶段 10：安装、更新、回滚

实现：

- `install.ps1`；
- 路径选择；
- 依赖检测；
- 配置备份；
- 更新检查；
- 中文 changelog；
- 本地快照；
- 升级失败回滚。

## 阶段 11：完整测试与发布候选

- 单元测试；
- 集成测试；
- GitHub 沙箱 E2E；
- Windows 干净用户测试；
- 故障注入；
- 安全检查；
- 文档校验。

通过后生成 Codex 独立测试输入包，但不得自行宣布正式发布。


---

<!-- 来源文件：11_Codex独立功能测试指令.md -->

# 11 Codex 独立功能测试指令

以下内容单独交给 Codex。

```text
你是 Agent Version Manager（AVM）的独立功能测试者。你不是开发者，不得默认相信 Claude Code 的阶段报告、自测结论或已知限制说明。

职责边界：
1. 第一轮只测试和报告，不修改正式代码。
2. Claude Code 修复后，你再次复测。
3. 同一严重问题连续两轮未解决时，你可提交强制修复方案，但仍不得直接修改正式代码。
4. 所有报告使用中文。

测试分两轮：

第一轮：开发目录回归测试
- 检查源码、依赖、测试、文档和安装脚本；
- 重跑全部测试；
- 检查测试是否真实覆盖外部行为；
- 执行静态分析和安全检查；
- 对状态机进行非法迁移测试；
- 对审批失效进行篡改测试；
- 对 Hooks 绕过和 Ruleset 兜底进行测试。

第二轮：全新克隆测试
- 从 GitHub 克隆到全新独立目录；
- 不复用开发虚拟环境、缓存、配置或凭据文件；
- 按用户手册安装；
- 初始化测试项目；
- 测试新空仓库和已有仓库；
- 分别通过 Claude Code、Hermes、Codex 包装入口执行任务；
- 验证中文确认；
- 验证代码任务强制 GitHub；
- 验证文档任务本地 doc-vN；
- 验证修改前备份和恢复；
- 验证任务中断、接管和废弃；
- 验证网络断开、认证失效、标签失败和 Release 失败；
- 验证批准后文件变化会失效；
- 验证 PR Squash、标签、Release 一一对应；
- 验证 Release 资产必须再次确认；
- 验证敏感文件会阻止发布；
- 验证工具更新和回滚。

恶意与误用测试：
- 尝试直接在 main 提交和推送；
- 尝试 git commit --no-verify；
- 尝试删除本地 Hook；
- 尝试修改 approval.json；
- 尝试复用废弃版本号；
- 尝试同时启动两个任务；
- 尝试使用过期接手报告；
- 尝试篡改文档备份；
- 尝试把 Token 写入日志；
- 尝试在 CI 中跳过检查。

报告格式：
- 环境；
- 版本和提交；
- 测试项；
- 步骤；
- 期望；
- 实际；
- 证据；
- 等级；
- 是否阻断发布；
- 最小复现；
- 修复建议。

缺陷等级：阻断级、严重级、一般级、建议级。

发布门槛：
以下能力必须全部通过：初始化、版本递增、PR/Squash/标签/Release、中文审批、审批失效、任务锁与恢复、文档备份与哈希、CI、三 Agent 适配、Hook 与远程兜底、敏感扫描、网络与发布异常恢复。
非核心界面问题可以进入后续版本。
```


---

<!-- 来源文件：12_测试矩阵与验收标准.md -->

# 12 测试矩阵与验收标准

## 1. 测试层级

- 单元测试：纯函数、模型、分类、版本号、哈希、模板。
- 组件测试：Git 仓库、Hooks、备份、审批、状态机。
- 集成测试：本地 Git + gh mock/沙箱。
- 端到端测试：真实测试 GitHub 仓库。
- 故障注入：网络、权限、进程中断、磁盘、冲突。
- 独立验收：Codex 两轮测试。

## 2. 必测矩阵

| 编号 | 场景 | 预期 |
|---|---|---|
| T001 | 非 Git 项目初始化 | 中文引导并创建私有仓库 |
| T002 | 空仓库基线 | 受控引导提交 + v1 + Release |
| T003 | 已有 v7 | 初始化使用 v8 |
| T004 | 未提交修改 | 生成差异并让用户选择 |
| T005 | 代码修改拒绝 GitHub | 任务取消，不允许修改 |
| T006 | 文档本地模式 | doc-vN + 修改前备份 |
| T007 | 修改 Word 的代码 | 按文档任务询问 |
| T008 | 同项目并发 | 第二任务被远程锁阻止 |
| T009 | 废弃 v8 | 下次为 v9 |
| T010 | 审批后改文件 | 批准失效 |
| T011 | 本地测试失败 | 只能草稿 PR |
| T012 | CI 失败 | 不得合并 |
| T013 | PR 合并后标签失败 | 发布未完成，阻塞后续任务 |
| T014 | Release 失败 | 原版本恢复发布，不新建版本 |
| T015 | 网络中断 | 本地工作保留，禁止完成发布 |
| T016 | gh 认证失效 | 中文阻断和恢复指引 |
| T017 | 敏感信息 | 阻止提交和推送 |
| T018 | 超过范围阈值 | 重新中文确认 |
| T019 | 文档备份篡改 | 恢复前校验失败 |
| T020 | 中断任务接管 | 用户选择后沿用原版本与分支 |
| T021 | 成功发布 | PR、Squash、tag、Release 一一对应 |
| T022 | 直接推 main | 本地与远程均阻止 |
| T023 | --no-verify | 本地可绕过但远程 Ruleset/CI 阻止 |
| T024 | 配置修改 | 先备份、展示差异、确认、可恢复 |
| T025 | 工具升级失败 | 自动回滚 |

## 3. 发布阻断条件

任一成立即不得发布：

- 核心状态机非法迁移；
- 版本号可复用或重复；
- 审批后内容可变化仍发布；
- 文档修改前备份缺失或无法恢复；
- 直接推送正式分支可绕过远程控制；
- 敏感信息进入仓库或日志；
- 发布失败后允许开始新版本；
- 三 Agent 任一适配不能触发预检；
- Codex 独立测试存在阻断级或严重级问题。

## 4. 覆盖率与证据

不以单一覆盖率数字代替质量。建议：

- 核心纯逻辑行覆盖率不低于 90%；
- 状态迁移分支覆盖率 100%；
- 每个异常状态至少一个故障注入测试；
- E2E 输出 PR、标签、Release 和恢复证据；
- Windows 安装从干净目录执行。

## 5. 第一版验收结论格式

```text
核心能力：通过/不通过
安全边界说明：完整/不完整
Windows 安装：通过/不通过
Claude Code：通过/不通过
Hermes：通过/不通过
Codex：通过/不通过
GitHub E2E：通过/不通过
文档备份恢复：通过/不通过
异常恢复：通过/不通过
阻断级问题：N
严重级问题：N
发布建议：允许/禁止
```


---

<!-- 来源文件：13_安装部署与使用手册.md -->

# 13 安装部署与使用手册

## 1. Windows 安装流程

1. 运行 `install.ps1`；
2. 检查 D 盘，默认 `D:\AgentVersionManager\`；
3. 若无 D 盘，推荐用户目录；
4. 检查 Python、Git、gh、Git LFS、PowerShell；
5. 展示需安装或修改内容；
6. 用户中文确认；
7. 建立独立虚拟环境；
8. 安装 AVM；
9. 添加用户级 PATH；
10. 备份并适配三个 Agent；
11. 运行 `avm doctor`。

任何全局配置修改必须先生成时间戳备份，永久保留。

## 2. 初始化项目

```powershell
cd D:\project
avm init-project
```

向导步骤：

- 项目名称；
- Git 状态；
- 默认分支确认；
- GitHub 仓库检查或私有仓库创建；
- 未提交修改处理；
- 敏感信息扫描；
- 文件类型和 LFS 建议；
- CI 建议；
- Ruleset 支持情况；
- 基线版本号；
- 中文发布说明；
- 用户批准；
- 发布基线。

## 3. 启动 Agent

```powershell
avm launch claude --project D:\project
avm launch hermes --project D:\project
avm launch codex --project D:\project
```

## 4. 查看状态

```powershell
avm status
avm status --json
```

显示：当前版本、下一个版本、活动任务、分支、PR、锁、测试、待归档文档记录和发布异常。

## 5. 文档本地任务

```powershell
avm document-start --files thesis.docx figure.drawio
```

工具先备份并校验，随后 Agent 才能修改。完成：

```powershell
avm document-complete
```

## 6. 中断恢复

```powershell
avm recover
```

先生成《中断任务接管报告》，然后由用户选择处理方式。

## 7. 更新工具

```powershell
avm update-check
```

有新版本时中文展示更新内容、兼容性、快照位置。用户确认后：

```powershell
avm update
```

失败自动回滚。

## 8. 恢复配置

```powershell
avm config-backup-list
avm config-restore
```

恢复和清理都必须中文确认。


---

<!-- 来源文件：14_严格审查结论与风险修正.md -->

# 14 严格审查结论与风险修正

## 1. 原始构想的主要缺陷

### 1.1 “每次询问是否提交”与“必须提交”冲突

修正：

- 代码、配置、项目描述等只询问“确认开始/取消任务”；
- 文档任务才询问是否启用正式 GitHub 流程。

### 1.2 每次复制代码文件会造成重复存储

修正：代码和配置由 Git 保存；不在版本目录复制。二进制文档因为 diff 能力有限，修改前额外备份。

### 1.3 “记录全过程思考逻辑”不可可靠执行

模型隐藏思维链不应作为交付物。修正为可审计的决策与执行记录。

### 1.4 只靠 Agent 自觉不可靠

修正为共享核心、包装入口、规则文件、Hooks、CI、Ruleset 多层机制。

### 1.5 Git Hooks 不是绝对强制

任何能使用 `--no-verify` 或删除 Hook 的主体可绕过。修正为远程 Ruleset 和必需 CI 兜底，并在产品说明中明确边界。

### 1.6 初始化空仓库无法先走 PR

必须允许一次受控引导提交，否则无法建立默认分支。该例外必须被审计和限定。

### 1.7 “合并后更新报告且仍在同一提交”存在事务矛盾

合并后才知道实际 Squash 哈希和 Release URL，但此时修改仓库报告会产生第二个提交。修正：

- 合并前报告保存预期发布信息；
- 实际远程对象写入 Release、全局状态和后续索引同步；
- 不为了补 URL 破坏一版本一提交。

### 1.8 废弃版本记录进入主分支会产生无版本提交

修正：废弃记录先保存在关闭 PR、任务分支和本地目录；下一个正式版本统一归档。不得创建“无版本审计提交”污染主分支。

### 1.9 文档本地版本可能长期未归档

当前选择是等待下一正式版本。风险是长期没有正式任务时记录只在本地。建议保留 `avm archive-pending-docs`，由用户主动触发一个正式项目版本进行归档，但不得自动触发。

### 1.10 GitHub 计划差异

私有仓库可用的 Ruleset、push ruleset 等能力可能受套餐影响。工具必须探测并报告，不得假设全部功能可用。

## 2. 仍无法彻底消除的风险

- 管理员可关闭 Ruleset；
- 高权限 Token 可绕开工具；
- Agent 可直接修改本地文件，AVM只能在提交和发布时阻止；
- 二进制文档恶意格式或内部宏需要额外安全扫描；
- 大型模型权重和数据集不适合直接 Git/LFS；
- 用户批准内容的身份真实性取决于本机安全。

## 3. 建议但未强制的后续增强

- Windows 服务形式的文件事件监控；
- 独立桌面审批界面；
- GitHub App 身份和最小权限 Token；
- 审批记录公钥签名；
- 远程审计数据库；
- 多项目并发调度；
- 组织级 Ruleset；
- SBOM、依赖漏洞和二进制宏扫描。

## 4. 严格结论

该计划在经过上述修正后具备可执行性。第一版必须避免宣称“所有 Agent 绝对无法绕过”。准确表述应为：

> AVM 对通过其包装入口和正常 Git/GitHub 权限模型运行的 Agent 提供强制、可审计的多层版本工作流；远程 Ruleset 和 CI 负责阻止大部分本地绕过，但不能对仓库管理员或泄露的高权限凭据提供绝对防护。


---

<!-- 来源文件：15_配置与报告模板.md -->

# 15 配置与报告模板

## 1. 项目配置模板

```yaml
schema_version: 1
project:
  name: "项目名称"
  root: "."
  github_repo: "owner/repo"
  default_branch: "main"

versioning:
  formal_prefix: "v"
  document_prefix: "doc-v"
  never_reuse_reserved: true
  one_active_task: true
  merge_strategy: "squash"

language:
  user_facing: "zh-CN"
  machine_identifiers: "ascii"

validation:
  commands:
    - name: "单元测试"
      command: ["python", "-m", "pytest"]
    - name: "格式检查"
      command: ["python", "-m", "ruff", "check", "."]

risk:
  extra_file_limit: 5
  expansion_ratio: 0.5
  sensitive_patterns: []
  high_risk_paths:
    - ".github/workflows/**"
    - "**/.env*"
    - "**/*.pem"
    - "**/*.key"

lfs:
  enabled: false
  patterns: []

agent_adapters:
  claude_code: true
  hermes: true
  codex: true
```

## 2. 当前任务模板

```json
{
  "schema_version": 1,
  "task_id": "uuid",
  "status": "MODIFYING",
  "version": "v8",
  "agent": "claude-code",
  "branch": "agent/v8-task-slug",
  "base_commit": "sha",
  "started_at": "ISO-8601",
  "expected_files": [],
  "remote_lock_ref": "refs/heads/avm/system-lock",
  "approval_id": null
}
```

## 3. 更新说明模板

```markdown
# v8 更新说明

## 版本目标

## 新增内容

## 修改内容

## 修复内容

## 删除内容

## 行为变化

## 兼容性影响

## 升级或迁移要求

## 已知限制
```

## 4. 决策与执行记录模板

```markdown
# 决策与执行记录

## 需求理解

## 关键假设

## 候选方案

## 采用方案及理由

## 未采用方案及理由

## 执行步骤

## 关键失败尝试

## 回退与修正

## 验证证据

## 遗留问题

## 历史回查记录
```

## 5. 接手项目审查报告模板

```markdown
# 最新接手项目审查报告

## 报告基准
- 正式版本：
- 正式分支：
- 基准提交：
- 生成时间：
- 生成 Agent：

## 当前项目目标

## 当前架构与关键模块

## 运行、构建和测试方式

## 最近一次版本变化

## 当前配置与约束

## 当前风险

## 遗留问题

## 未完成任务

## 待归档文档记录

## 历史索引

## 何时必须回查更早版本
```

## 6. 最终审批界面模板

```text
【版本发布审批】

项目：
版本：
任务分支：
PR：
基准提交：
修改文件数：
验证结果：

提交标题：
提交正文：

PR 标题：
PR 正文：

Release 标题：
Release 正文：

拟上传资产：

请选择：
[批准执行]
[修改上述内容]
[取消发布]
```

## 7. 中断任务接管报告模板

```markdown
# 中断任务接管报告

## 原任务
## 原 Agent
## 版本与分支
## 当前锁
## 工作区修改
## 未推送提交
## PR 状态
## 测试状态
## 文档备份
## 已完成内容
## 未完成内容
## 风险
## 可选处理
- 继续
- 回滚
- 废弃
- 暂不处理
```
