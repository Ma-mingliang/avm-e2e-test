"""AVM validate 命令"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

console = Console()


def run_validate(project_path: Path, json_output: bool = False) -> bool:
    """运行验证"""
    console.print("[bold]运行验证[/bold]")
    console.print("验证功能将在后续阶段实现")
    return True
