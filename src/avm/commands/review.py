"""AVM prepare-review 命令"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def run_prepare_review(project_path: Path) -> bool:
    """准备审阅材料"""
    console.print("[bold]准备审阅材料[/bold]")
    console.print("审阅材料准备功能将在后续阶段实现")
    return True
