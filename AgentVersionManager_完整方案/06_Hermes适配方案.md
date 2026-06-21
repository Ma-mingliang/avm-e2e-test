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
