"""AVM approve 命令测试"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from avm.commands.approve import run_approve
from avm.core.io import atomic_write_json
from avm.core.paths import get_task_lock_path
from avm.models import TaskStatus


@pytest.fixture
def project_dir(tmp_path):
    """创建项目目录"""
    version_dir = tmp_path / "版本管理"
    version_dir.mkdir(parents=True)
    return tmp_path


def _create_lock(project_dir: Path, status: str) -> None:
    """创建任务锁"""
    lock_path = get_task_lock_path(project_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(lock_path, {
        "schema_version": 1,
        "status": status.upper(),
        "version": "v1",
        "agent": "claude-code",
        "branch": "agent/v1",
        "base_commit": "abc123",
        "started_at": "2024-01-01T00:00:00+00:00",
        "expected_files": [],
    })


class TestRunApprove:
    """approve 命令测试"""

    def test_approve_start_success(self, project_dir):
        """测试开始审批成功"""
        _create_lock(project_dir, "WAIT_START_APPROVAL")

        result = run_approve(project_dir, approver="test-user")
        assert result is True

    def test_approve_final_success(self, project_dir):
        """测试最终审批成功"""
        _create_lock(project_dir, "WAIT_FINAL_APPROVAL")

        result = run_approve(project_dir, approver="test-user")
        assert result is True

    def test_approve_wrong_state(self, project_dir):
        """测试错误状态"""
        _create_lock(project_dir, "RESERVED")

        result = run_approve(project_dir)
        assert result is False

    def test_approve_json_output(self, project_dir, capsys):
        """测试 JSON 输出"""
        _create_lock(project_dir, "WAIT_START_APPROVAL")

        result = run_approve(project_dir, approver="test-user", json_output=True)
        assert result is True

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert data["approval_id"] is not None
