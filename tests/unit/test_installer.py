"""AVM 安装器测试"""

import pytest
import json
from pathlib import Path

from avm.update.installer import Installer


@pytest.fixture
def temp_install_dir(tmp_path):
    """创建临时安装目录"""
    return tmp_path / "install"


class TestInstaller:
    """安装器测试"""

    def test_get_current_version_not_installed(self, temp_install_dir):
        """测试获取未安装版本"""
        installer = Installer(temp_install_dir)
        assert installer.get_current_version() == "not installed"

    def test_get_current_version_installed(self, temp_install_dir):
        """测试获取已安装版本"""
        installer = Installer(temp_install_dir)
        temp_install_dir.mkdir(parents=True)
        installer._save_version("1.0.0")

        assert installer.get_current_version() == "1.0.0"

    def test_save_version(self, temp_install_dir):
        """测试保存版本"""
        installer = Installer(temp_install_dir)
        temp_install_dir.mkdir(parents=True)
        installer._save_version("2.0.0")

        version_file = temp_install_dir / "version.json"
        assert version_file.exists()

        data = json.loads(version_file.read_text(encoding="utf-8"))
        assert data["version"] == "2.0.0"

    def test_backup_current(self, temp_install_dir):
        """测试备份当前版本"""
        installer = Installer(temp_install_dir)
        temp_install_dir.mkdir(parents=True)
        installer._save_version("1.0.0")

        backup_path = installer._backup_current()
        assert backup_path.exists()
        assert (backup_path / "version.json").exists()

    def test_list_backups_empty(self, temp_install_dir):
        """测试列出空备份"""
        installer = Installer(temp_install_dir)
        assert installer._list_backups() == []

    def test_list_backups(self, temp_install_dir):
        """测试列出备份"""
        installer = Installer(temp_install_dir)
        temp_install_dir.mkdir(parents=True)
        installer._save_version("1.0.0")
        installer._backup_current()

        backups = installer._list_backups()
        assert len(backups) == 1
        assert backups[0]["name"].startswith("backup_1.0.0_")

    def test_rollback_no_backup(self, temp_install_dir):
        """测试无备份回滚"""
        installer = Installer(temp_install_dir)
        result = installer.rollback()

        assert not result["success"]
        assert any(s["status"] == "error" for s in result["steps"])

    def test_rollback_with_backup(self, temp_install_dir):
        """测试有备份回滚"""
        installer = Installer(temp_install_dir)
        temp_install_dir.mkdir(parents=True)
        installer._save_version("1.0.0")
        installer._backup_current()

        result = installer.rollback()
        assert result["success"]
