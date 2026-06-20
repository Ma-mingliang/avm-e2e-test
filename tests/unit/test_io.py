"""AVM IO工具测试"""

import json
import pytest
import yaml
from pathlib import Path

from avm.core.io import (
    atomic_write_text,
    atomic_write_json,
    atomic_write_yaml,
    read_json,
    read_yaml,
    read_text,
)
from avm.exceptions import AVMError


class TestAtomicWrite:
    """原子写入测试"""

    def test_atomic_write_text(self, tmp_path):
        """测试原子写入文本"""
        target = tmp_path / "test.txt"
        atomic_write_text(target, "hello world")

        assert target.exists()
        assert target.read_text(encoding="utf-8") == "hello world"

    def test_atomic_write_text_overwrite(self, tmp_path):
        """测试原子写入覆盖"""
        target = tmp_path / "test.txt"
        atomic_write_text(target, "first")
        atomic_write_text(target, "second")

        assert target.read_text(encoding="utf-8") == "second"

    def test_atomic_write_json(self, tmp_path):
        """测试原子写入JSON"""
        target = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        atomic_write_json(target, data)

        assert target.exists()
        with open(target, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_atomic_write_yaml(self, tmp_path):
        """测试原子写入YAML"""
        target = tmp_path / "test.yaml"
        data = {"key": "value", "number": 42}
        atomic_write_yaml(target, data)

        assert target.exists()
        with open(target, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_atomic_write_creates_parent_dirs(self, tmp_path):
        """测试原子写入创建父目录"""
        target = tmp_path / "sub" / "dir" / "test.txt"
        atomic_write_text(target, "hello")

        assert target.exists()
        assert target.read_text(encoding="utf-8") == "hello"


class TestRead:
    """读取测试"""

    def test_read_json(self, tmp_path):
        """测试读取JSON"""
        target = tmp_path / "test.json"
        data = {"key": "value"}
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded = read_json(target)
        assert loaded == data

    def test_read_json_not_found(self, tmp_path):
        """测试读取不存在的JSON"""
        with pytest.raises(AVMError) as exc_info:
            read_json(tmp_path / "nonexistent.json")
        assert "文件不存在" in str(exc_info.value)

    def test_read_json_invalid(self, tmp_path):
        """测试读取无效JSON"""
        target = tmp_path / "invalid.json"
        target.write_text("not json", encoding="utf-8")

        with pytest.raises(AVMError) as exc_info:
            read_json(target)
        assert "JSON格式错误" in str(exc_info.value)

    def test_read_yaml(self, tmp_path):
        """测试读取YAML"""
        target = tmp_path / "test.yaml"
        data = {"key": "value"}
        with open(target, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

        loaded = read_yaml(target)
        assert loaded == data

    def test_read_yaml_not_found(self, tmp_path):
        """测试读取不存在的YAML"""
        with pytest.raises(AVMError) as exc_info:
            read_yaml(tmp_path / "nonexistent.yaml")
        assert "文件不存在" in str(exc_info.value)

    def test_read_text(self, tmp_path):
        """测试读取文本"""
        target = tmp_path / "test.txt"
        target.write_text("hello", encoding="utf-8")

        content = read_text(target)
        assert content == "hello"

    def test_read_text_not_found(self, tmp_path):
        """测试读取不存在的文本"""
        with pytest.raises(AVMError) as exc_info:
            read_text(tmp_path / "nonexistent.txt")
        assert "文件不存在" in str(exc_info.value)
