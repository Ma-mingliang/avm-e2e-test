"""AVM status 和 checkpoint 命令测试"""

import pytest
import subprocess
import json
from pathlib import Path

from avm.commands.status import run_status, _get_status
from avm.commands.checkpoint import run_checkpoint, _do_checkpoint
from avm.core.locking import TaskLocker
from avm.models import TaskLock, TaskStatus, AgentType


@pytest.fixture
def git_project(tmp_path):
    """创建临时 Git 项目"""
    repo = tmp_path / "repo"
    repo.mkdir()

    # 初始化 Git 仓库
    subprocess.run(["git", "init"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, capture_output=True)

    # 创建 .gitignore
    (repo / ".gitignore").write_text("版本管理/\n", encoding="utf-8")

    # 创建初始提交
    (repo / "README.md").write_text("# Test", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "初始提交"], cwd=repo, capture_output=True)

    return repo


@pytest.fixture
def project_with_lock(git_project):
    """创建带任务锁的项目"""
    locker = TaskLocker(git_project)
    lock = TaskLock(
        status=TaskStatus.RESERVED,
        version="v1",
        agent=AgentType.CLAUDE_CODE,
        branch="agent/v1-test",
        base_commit="abc123",
    )
    locker.acquire_lock(lock)
    return git_project


class TestStatus:
    """status 命令测试"""

    def test_get_status_no_lock(self, git_project):
        """测试无任务锁时的状态"""
        result = _get_status(git_project)

        assert result["git"]["is_repo"]
        assert not result["has_active_task"]
        assert "version" in result

    def test_get_status_with_lock(self, project_with_lock):
        """测试有任务锁时的状态"""
        result = _get_status(project_with_lock)

        assert result["git"]["is_repo"]
        assert result["has_active_task"]
        assert result["task"]["version"] == "v1"
        assert result["task"]["agent"] == "claude-code"

    def test_get_status_not_git(self, tmp_path):
        """测试非 Git 项目"""
        result = _get_status(tmp_path)

        assert not result["git"]["is_repo"]

    def test_status_json_output(self, git_project, capsys):
        """测试 JSON 输出"""
        run_status(git_project, json_output=True)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "project_path" in output
        assert "git" in output

    def test_status_has_hooks_info(self, git_project):
        """测试包含 Hooks 信息"""
        result = _get_status(git_project)
        assert "hooks" in result


class TestCheckpoint:
    """checkpoint 命令测试"""

    def test_checkpoint_no_lock(self, git_project):
        """测试无任务锁时的提交"""
        result = _do_checkpoint(git_project, "测试提交")

        assert not result["success"]
        assert any(s["status"] == "error" for s in result["steps"])

    def test_checkpoint_no_changes(self, project_with_lock):
        """测试无修改时的提交"""
        result = _do_checkpoint(project_with_lock, "测试提交")

        assert result["success"]
        # 应该有 "没有未提交的修改" 的警告
        assert any(s["status"] == "warn" for s in result["steps"])

    def test_checkpoint_with_changes(self, project_with_lock):
        """测试有修改时的提交"""
        # 创建新文件
        (project_with_lock / "new_file.txt").write_text("新内容", encoding="utf-8")

        result = _do_checkpoint(project_with_lock, "添加新文件")

        assert result["success"]
        assert any(s["step"] == "commit" and s["status"] == "ok" for s in result["steps"])

    def test_checkpoint_json_output(self, project_with_lock, capsys):
        """测试 JSON 输出"""
        run_checkpoint(project_with_lock, "测试提交", json_output=True)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "success" in output
