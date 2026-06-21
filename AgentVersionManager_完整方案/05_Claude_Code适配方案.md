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
