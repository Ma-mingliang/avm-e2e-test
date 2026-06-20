"""AVM start 命令"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()


def run_start(project_path: Path, version: str, json_output: bool = False) -> bool:
    """开始任务"""
    console.print("[bold]开始任务[/bold]")
    console.print("任务开始功能将在后续阶段实现")
    return True
