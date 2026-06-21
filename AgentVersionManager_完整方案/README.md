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
