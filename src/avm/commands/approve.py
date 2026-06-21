"""AVM approve 命令"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from rich.console import Console

from ..core.approval import ApprovalManager
from ..core.state_machine import StateMachine
from ..models import ApprovalType, TaskStatus

console = Console()


def run_approve(
    project_path: Path,
    approver: Optional[str] = None,
    notes: str = "",
    json_output: bool = False,
) -> bool:
    """用户审批

    Args:
        project_path: 项目路径
        approver: 审批人（默认从环境获取）
        notes: 审批备注
        json_output: JSON 输出格式

    Returns:
        是否成功
    """
    result = {
        "success": False,
        "approval_id": None,
        "status": None,
        "steps": [],
    }

    # 1. 加载状态机
    sm = StateMachine(project_path)
    sm.load()

    current = sm.current_status
    task_lock = sm.task_lock

    # 2. 检查是否需要审批
    if current not in (TaskStatus.WAIT_START_APPROVAL, TaskStatus.WAIT_FINAL_APPROVAL):
        result["steps"].append({
            "step": "check_state",
            "status": "error",
            "message": f"当前状态为 {current.value}，不需要审批",
        })
        _output(result, json_output)
        return False

    # 3. 确定审批类型
    if current == TaskStatus.WAIT_START_APPROVAL:
        approval_type = ApprovalType.START
        next_status = TaskStatus.RESERVED
    else:
        approval_type = ApprovalType.FINAL_RELEASE
        next_status = TaskStatus.PR_READY

    # 4. 获取审批人
    if not approver:
        import os
        approver = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    # 5. 创建审批记录
    approval_mgr = ApprovalManager(project_path)
    try:
        record = approval_mgr.create_approval(
            task_lock=task_lock,
            approval_type=approval_type,
            approver=approver,
            notes=notes,
        )
        result["approval_id"] = record.approval_id
        result["steps"].append({
            "step": "create_approval",
            "status": "ok",
            "message": f"审批记录已创建: {record.approval_id}",
        })
    except Exception as e:
        result["steps"].append({
            "step": "create_approval",
            "status": "error",
            "message": f"创建审批记录失败: {e}",
        })
        _output(result, json_output)
        return False

    # 6. 状态转换
    try:
        sm.transition(next_status, {"approval_id": record.approval_id})
        result["status"] = next_status.value
        result["steps"].append({
            "step": "state_transition",
            "status": "ok",
            "message": f"状态已转换为 {next_status.value}",
        })
    except Exception as e:
        result["steps"].append({
            "step": "state_transition",
            "status": "error",
            "message": f"状态转换失败: {e}",
        })
        _output(result, json_output)
        return False

    result["success"] = True
    _output(result, json_output)
    return True


def _output(result: dict, json_output: bool) -> None:
    """输出结果"""
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            console.print("[bold green]审批通过[/bold green]")
            console.print(f"  审批ID: {result['approval_id']}")
            console.print(f"  新状态: {result['status']}")
        else:
            console.print("[bold red]审批失败[/bold red]")
            for step in result["steps"]:
                if step["status"] == "error":
                    console.print(f"  [red]✗ {step['message']}[/red]")
