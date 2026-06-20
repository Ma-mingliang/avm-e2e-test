"""AVM Agent 适配器测试"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from avm.adapters.base import AgentAdapter
from avm.adapters.claude_code import ClaudeCodeAdapter
from avm.adapters.hermes import HermesAdapter
from avm.adapters.codex import CodexAdapter
from avm.adapters.factory import get_adapter, get_all_adapters, get_available_adapters, detect_agent
from avm.models import AgentType, TaskLock, TaskStatus


@pytest.fixture
def temp_project(tmp_path):
    """创建临时项目目录"""
    return tmp_path


class TestClaudeCodeAdapter:
    """Claude Code 适配器测试"""

    def test_agent_type(self, temp_project):
        """测试 Agent 类型"""
        adapter = ClaudeCodeAdapter(temp_project)
        assert adapter.agent_type == AgentType.CLAUDE_CODE

    def test_name(self, temp_project):
        """测试名称"""
        adapter = ClaudeCodeAdapter(temp_project)
        assert adapter.name == "Claude Code"

    def test_is_available(self, temp_project):
        """测试可用性检查"""
        adapter = ClaudeCodeAdapter(temp_project)
        # 不检查实际可用性，只测试方法不抛异常
        result = adapter.is_available()
        assert isinstance(result, bool)

    def test_get_version(self, temp_project):
        """测试获取版本"""
        adapter = ClaudeCodeAdapter(temp_project)
        version = adapter.get_version()
        assert isinstance(version, str)

    def test_preflight_check(self, temp_project):
        """测试预检"""
        adapter = ClaudeCodeAdapter(temp_project)
        result = adapter.preflight_check()
        assert "passed" in result
        assert "checks" in result

    def test_start_task(self, temp_project):
        """测试开始任务"""
        adapter = ClaudeCodeAdapter(temp_project)
        lock = TaskLock(
            status=TaskStatus.RESERVED,
            version="v1",
            agent=AgentType.CLAUDE_CODE,
            branch="agent/v1-test",
            base_commit="abc123",
        )
        assert adapter.start_task(lock)

    def test_validate(self, temp_project):
        """测试验证"""
        adapter = ClaudeCodeAdapter(temp_project)
        result = adapter.validate()
        assert "passed" in result

    def test_prepare_review(self, temp_project):
        """测试准备审查"""
        adapter = ClaudeCodeAdapter(temp_project)
        result = adapter.prepare_review()
        assert "passed" in result

    def test_get_status(self, temp_project):
        """测试获取状态"""
        adapter = ClaudeCodeAdapter(temp_project)
        status = adapter.get_status()
        assert "agent" in status
        assert "available" in status

    def test_get_adapter_info(self, temp_project):
        """测试获取适配器信息"""
        adapter = ClaudeCodeAdapter(temp_project)
        info = adapter.get_adapter_info()
        assert info["agent_type"] == "claude-code"
        assert info["name"] == "Claude Code"


class TestHermesAdapter:
    """Hermes 适配器测试"""

    def test_agent_type(self, temp_project):
        """测试 Agent 类型"""
        adapter = HermesAdapter(temp_project)
        assert adapter.agent_type == AgentType.HERMES

    def test_name(self, temp_project):
        """测试名称"""
        adapter = HermesAdapter(temp_project)
        assert adapter.name == "Hermes"


class TestCodexAdapter:
    """Codex 适配器测试"""

    def test_agent_type(self, temp_project):
        """测试 Agent 类型"""
        adapter = CodexAdapter(temp_project)
        assert adapter.agent_type == AgentType.CODEX

    def test_name(self, temp_project):
        """测试名称"""
        adapter = CodexAdapter(temp_project)
        assert adapter.name == "Codex"


class TestAdapterFactory:
    """适配器工厂测试"""

    def test_get_adapter_claude_code(self, temp_project):
        """测试获取 Claude Code 适配器"""
        adapter = get_adapter(AgentType.CLAUDE_CODE, temp_project)
        assert isinstance(adapter, ClaudeCodeAdapter)

    def test_get_adapter_hermes(self, temp_project):
        """测试获取 Hermes 适配器"""
        adapter = get_adapter(AgentType.HERMES, temp_project)
        assert isinstance(adapter, HermesAdapter)

    def test_get_adapter_codex(self, temp_project):
        """测试获取 Codex 适配器"""
        adapter = get_adapter(AgentType.CODEX, temp_project)
        assert isinstance(adapter, CodexAdapter)

    def test_get_all_adapters(self, temp_project):
        """测试获取所有适配器"""
        adapters = get_all_adapters(temp_project)
        assert len(adapters) == 3

    def test_get_available_adapters(self, temp_project):
        """测试获取可用适配器"""
        adapters = get_available_adapters(temp_project)
        # 可能没有可用的适配器
        assert isinstance(adapters, list)

    def test_detect_agent(self, temp_project):
        """测试自动检测 Agent"""
        agent = detect_agent(temp_project)
        # 可能没有可用的 Agent
        assert agent is None or isinstance(agent, AgentAdapter)
