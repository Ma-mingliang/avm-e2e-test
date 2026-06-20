"""AVM config 命令"""

from __future__ import annotations

import json

from rich.console import Console

console = Console()


def run_config_backup_list(json_output: bool = False) -> bool:
    """列出配置备份"""
    console.print("[bold]配置备份列表[/bold]")
    console.print("配置备份列表功能将在后续阶段实现")
    return True


def run_config_restore(backup_id: str) -> bool:
    """恢复配置"""
    console.print("[bold]恢复配置[/bold]")
    console.print("配置恢复功能将在后续阶段实现")
    return True
