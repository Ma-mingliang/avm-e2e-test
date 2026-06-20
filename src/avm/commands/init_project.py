"""AVM init-project 命令"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

from ..config import create_default_config, save_project_config
from ..core.paths import get_version_dir, get_task_lock_path
from ..git.ops import GitOps

console = Console()


def run_init_project(project_path: Path, name: str | None = None, json_output: bool = False) -> bool:
    """初始化项目

    Args:
        project_path: 项目路径
        name: 项目名称（可选）
        json_output: 是否输出 JSON

    Returns:
        是否成功
    """
    try:
        result = _init_project(project_path, name)

        if json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_result(result)

        return result["success"]
    except Exception as e:
        if json_output:
            print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
        else:
            console.print(f"[red]错误: {e}[/red]")
        return False


def _init_project(project_path: Path, name: str | None) -> Dict[str, Any]:
    """执行项目初始化

    Args:
        project_path: 项目路径
        name: 项目名称

    Returns:
        初始化结果
    """
    project_path = Path(project_path).resolve()
    results = {
        "success": True,
        "project_path": str(project_path),
        "steps": [],
    }

    # 1. 检查是否为 Git 仓库
    git = GitOps(project_path)
    if not git.detect_repo():
        results["steps"].append({
            "step": "git_check",
            "status": "error",
            "message": "项目目录不是 Git 仓库",
        })
        results["success"] = False
        return results

    results["steps"].append({
        "step": "git_check",
        "status": "ok",
        "message": "Git 仓库检测通过",
    })

    # 2. 创建版本管理目录结构
    version_dir = get_version_dir(project_path)
    dirs_created = []

    # 主目录
    version_dir.mkdir(parents=True, exist_ok=True)
    dirs_created.append(str(version_dir))

    # 子目录
    subdirs = [
        "正式版本",
        "文档版本",
        "备份",
        "审批",
        "交接",
    ]
    for subdir in subdirs:
        sub_path = version_dir / subdir
        sub_path.mkdir(parents=True, exist_ok=True)
        dirs_created.append(str(sub_path))

    results["steps"].append({
        "step": "create_dirs",
        "status": "ok",
        "message": f"创建目录结构: {len(dirs_created)} 个目录",
        "dirs": dirs_created,
    })

    # 3. 创建配置文件
    project_name = name or project_path.name
    config = create_default_config(project_path, project_name)
    save_project_config(config, project_path)

    results["steps"].append({
        "step": "create_config",
        "status": "ok",
        "message": f"创建配置文件: {version_dir / '配置.yaml'}",
    })

    # 4. 创建版本索引
    index_path = version_dir / "版本索引.json"
    if not index_path.exists():
        index = {
            "schema_version": 1,
            "project_name": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "formal_versions": [],
            "document_versions": [],
            "abandoned_versions": [],
            "pending_archives": [],
        }
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        results["steps"].append({
            "step": "create_index",
            "status": "ok",
            "message": f"创建版本索引: {index_path}",
        })
    else:
        results["steps"].append({
            "step": "create_index",
            "status": "skip",
            "message": "版本索引已存在",
        })

    # 5. 安装 Git Hooks
    try:
        if git.install_hooks():
            hooks_status = git.check_hooks()
            installed = [k for k, v in hooks_status.items() if v]
            results["steps"].append({
                "step": "install_hooks",
                "status": "ok",
                "message": f"安装 Git Hooks: {', '.join(installed)}",
            })
        else:
            results["steps"].append({
                "step": "install_hooks",
                "status": "warn",
                "message": "Git Hooks 安装失败（可手动安装）",
            })
    except Exception as e:
        results["steps"].append({
            "step": "install_hooks",
            "status": "warn",
            "message": f"Git Hooks 安装异常: {e}",
        })

    # 6. 创建 README（如果不存在）
    readme_path = version_dir / "README.md"
    if not readme_path.exists():
        readme_content = f"""# {project_name} - 版本管理

本目录由 Agent Version Manager (AVM) 管理。

## 目录结构

- `正式版本/` - 正式版本记录
- `文档版本/` - 文档版本记录
- `备份/` - 文件备份
- `审批/` - 审批记录
- `交接/` - 交接报告
- `版本索引.json` - 版本索引
- `配置.yaml` - 项目配置

## 使用方法

使用 AVM CLI 管理版本：

```bash
avm status          # 查看状态
avm preflight       # 预检
avm start           # 开始任务
avm validate        # 验证
avm publish         # 发布
```
"""
        readme_path.write_text(readme_content, encoding="utf-8")
        results["steps"].append({
            "step": "create_readme",
            "status": "ok",
            "message": f"创建 README: {readme_path}",
        })

    # 7. 创建 .gitignore（如果不存在）
    gitignore_path = version_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = """# AVM 临时文件
*.tmp
*.lock
__pycache__/

# 任务锁（本地）
任务锁.json
"""
        gitignore_path.write_text(gitignore_content, encoding="utf-8")
        results["steps"].append({
            "step": "create_gitignore",
            "status": "ok",
            "message": f"创建 .gitignore: {gitignore_path}",
        })

    return results


def _print_result(result: Dict[str, Any]) -> None:
    """打印初始化结果"""
    if result["success"]:
        console.print("[bold green]项目初始化成功[/bold green]")
    else:
        console.print("[bold red]项目初始化失败[/bold red]")

    console.print(f"项目路径: {result['project_path']}")
    console.print("")

    for step in result.get("steps", []):
        status = step["status"]
        message = step["message"]

        if status == "ok":
            icon = "[green]✓[/green]"
        elif status == "warn":
            icon = "[yellow]⚠[/yellow]"
        elif status == "error":
            icon = "[red]✗[/red]"
        elif status == "skip":
            icon = "[dim]-[/dim]"
        else:
            icon = "?"

        console.print(f"  {icon} {message}")
