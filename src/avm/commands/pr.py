"""AVM PR 命令"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()


def run_create_pr(project_path: Path, draft: bool, json_output: bool = False) -> bool:
    """创建PR"""
    console.print("[bold]创建PR[/bold]")
    console.print("PR创建功能将在后续阶段实现")
    return True


def run_merge(project_path: Path) -> bool:
    """合并PR"""
    console.print("[bold]合并PR[/bold]")
    console.print("PR合并功能将在后续阶段实现")
    return True
