"""AVM preflight 命令"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()


def run_preflight(project_path: Path, agent: str, task: str, json_output: bool = False) -> bool:
    """修改前预检"""
    console.print("[bold]修改前预检[/bold]")
    console.print("预检功能将在后续阶段实现")
    return True
