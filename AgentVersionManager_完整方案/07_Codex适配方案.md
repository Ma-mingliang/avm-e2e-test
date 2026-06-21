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
