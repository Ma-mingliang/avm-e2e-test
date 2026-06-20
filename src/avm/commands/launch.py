"""AVM launch 命令"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def run_launch(agent_name: str, project_path: Path) -> bool:
    """启动Agent"""
    console.print(f"[bold]启动 {agent_name}[/bold]")
    console.print("Agent启动功能将在后续阶段实现")
    return True
