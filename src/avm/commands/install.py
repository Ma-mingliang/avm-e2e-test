"""AVM install 命令"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def run_install(install_path: Path | None = None) -> bool:
    """安装AVM"""
    console.print("[bold]AVM 安装[/bold]")
    console.print("安装功能将在后续阶段实现")
    return True
