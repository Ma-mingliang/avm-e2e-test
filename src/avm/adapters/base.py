"""AVM Agent 适配器基类"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import AgentType, TaskLock, TaskStatus


class AgentAdapter(ABC):
    """Agent 适配器基类

    所有 Agent 适配器必须继承此类并实现抽象方法。
    """

    def __init__(self, project_root: Path):
        """初始化适配器

        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """返回 Agent 类型"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """返回 Agent 名称"""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """检查 Agent 是否可用

        Returns:
            是否可用
        """
        ...

    @abstractmethod
    def get_version(self) -> str:
        """获取 Agent 版本

        Returns:
            版本字符串
        """
        ...

    @abstractmethod
    def preflight_check(self) -> Dict[str, Any]:
        """预检

        Returns:
            检查结果
        """
        ...

    @abstractmethod
    def start_task(self, task_lock: TaskLock) -> bool:
        """开始任务

        Args:
            task_lock: 任务锁

        Returns:
            是否成功
        """
        ...

    @abstractmethod
    def checkpoint(self, message: str) -> bool:
        """阶段提交

        Args:
            message: 提交消息

        Returns:
            是否成功
        """
        ...

    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """验证

        Returns:
            验证结果
        """
        ...

    @abstractmethod
    def prepare_review(self) -> Dict[str, Any]:
        """准备审查

        Returns:
            审查准备结果
        """
        ...

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取状态

        Returns:
            状态信息
        """
        ...

    def get_adapter_info(self) -> Dict[str, Any]:
        """获取适配器信息

        Returns:
            适配器信息
        """
        return {
            "agent_type": self.agent_type.value if hasattr(self.agent_type, "value") else str(self.agent_type),
            "name": self.name,
            "available": self.is_available(),
            "version": self.get_version() if self.is_available() else None,
        }
