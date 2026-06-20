"""AVM recovery 命令"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def run_resume(project_path: Path) -> bool:
    """恢复中断任务"""
    console.print("[bold]恢复中断任务[/bold]")
    console.print("任务恢复功能将在后续阶段实现")
    return True


def run_abandon(project_path: Path) -> bool:
    """废弃任务"""
    console.print("[bold]废弃任务[/bold]")
    console.print("任务废弃功能将在后续阶段实现")
    return True


def run_recover(project_path: Path) -> bool:
    """恢复任务"""
    console.print("[bold]恢复任务[/bold]")
    console.print("任务恢复功能将在后续阶段实现")
    return True
