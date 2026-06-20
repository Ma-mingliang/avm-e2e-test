"""AVM publish 命令"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def run_publish(project_path: Path) -> bool:
    """发布版本"""
    console.print("[bold]发布版本[/bold]")
    console.print("版本发布功能将在后续阶段实现")
    return True
