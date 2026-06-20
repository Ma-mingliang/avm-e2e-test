"""AVM backup 命令"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()


def run_backup_list(project_path: Path, json_output: bool = False) -> bool:
    """列出备份"""
    console.print("[bold]备份列表[/bold]")
    console.print("备份列表功能将在后续阶段实现")
    return True


def run_backup_restore(project_path: Path, backup_id: str) -> bool:
    """恢复备份"""
    console.print("[bold]恢复备份[/bold]")
    console.print("备份恢复功能将在后续阶段实现")
    return True
