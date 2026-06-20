"""AVM approve 命令"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()


def run_approve(project_path: Path, json_output: bool = False) -> bool:
    """用户审批"""
    console.print("[bold]用户审批[/bold]")
    console.print("审批功能将在后续阶段实现")
    return True
