"""
IDE Integration Module
~~~~~~~~~~~~~~~~~~~~~~

Provides integration with various IDEs and code editors.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class IDEIntegration:
    """Base class for IDE integrations."""

    def __init__(self):
        self.config_dir = Path.home() / ".ai-code-reviewer"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_secure_permissions()

    def _ensure_secure_permissions(self):
        """Ensure configuration directory has secure permissions."""
        try:
            # Set directory to 0o700 (rwx------)
            os.chmod(self.config_dir, 0o700)
            logger.info(f"Secured config directory: {self.config_dir}")
        except Exception as e:
            logger.warning(f"Failed to set secure permissions: {e}")

    def _write_file_secure(self, file_path: Path, content: str, executable: bool = False):
        """
        Write file with secure permissions.

        Args:
            file_path: Path to file
            content: Content to write
            executable: Whether file should be executable
        """
        # Write file
        file_path.write_text(content)

        # Set secure permissions
        if executable:
            # Executable files: 0o750 (rwxr-x---)
            # Owner can read/write/execute, group can read/execute
            os.chmod(file_path, 0o750)
            logger.info(f"Created executable file: {file_path} (permissions: 0o750)")
        else:
            # Regular files: 0o640 (rw-r-----)
            # Owner can read/write, group can read
            os.chmod(file_path, 0o640)
            logger.info(f"Created file: {file_path} (permissions: 0o640)")


class VSCodeIntegration(IDEIntegration):
    """Visual Studio Code integration."""

    def __init__(self):
        super().__init__()
        self.vscode_dir = self._get_vscode_dir()

    def _get_vscode_dir(self) -> Optional[Path]:
        """Get VS Code configuration directory."""
        if sys.platform == "win32":
            vscode_dir = Path(os.getenv("APPDATA")) / "Code" / "User"
        elif sys.platform == "darwin":
            vscode_dir = Path.home() / "Library" / "Application Support" / "Code" / "User"
        else:
            vscode_dir = Path.home() / ".config" / "Code" / "User"

        return vscode_dir if vscode_dir.exists() else None

    def install_extension(self) -> bool:
        """
        Install VS Code extension.

        Returns:
            bool: True if successful
        """
        try:
            extension_path = Path(__file__).parent.parent / "vscode-extension"

            if not extension_path.exists():
                logger.warning("VS Code extension not found")
                return False

            result = subprocess.run(
                ["code", "--install-extension", str(extension_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info("VS Code extension installed successfully")
                return True
            else:
                logger.error(f"Failed to install extension: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error installing VS Code extension: {e}")
            return False

    def configure_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """
        Configure VS Code settings.

        Args:
            settings_dict: Settings to apply

        Returns:
            bool: True if successful
        """
        if not self.vscode_dir:
            logger.error("VS Code configuration directory not found")
            return False

        try:
            settings_file = self.vscode_dir / "settings.json"

            # Read existing settings
            existing_settings = {}
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    existing_settings = json.load(f)

            # Merge settings
            existing_settings.update(
                {
                    "aiCodeReviewer.enabled": True,
                    "aiCodeReviewer.apiUrl": f"http://localhost:{settings.port}",
                    "aiCodeReviewer.autoReview": settings_dict.get("auto_review", True),
                    **settings_dict,
                }
            )

            # Write settings with secure permissions
            self._write_file_secure(
                settings_file, json.dumps(existing_settings, indent=2), executable=False
            )

            logger.info("VS Code settings configured successfully")
            return True

        except Exception as e:
            logger.error(f"Error configuring VS Code settings: {e}")
            return False


class GitHooksIntegration(IDEIntegration):
    """Git hooks integration."""

    def __init__(self, repo_path: Optional[Path] = None):
        super().__init__()
        self.repo_path = repo_path or Path.cwd()
        self.hooks_dir = self.repo_path / ".git" / "hooks"

    def install_pre_commit_hook(self) -> bool:
        """
        Install pre-commit hook for code review.

        Returns:
            bool: True if successful
        """
        if not self.hooks_dir.exists():
            logger.error(f"Git hooks directory not found: {self.hooks_dir}")
            return False

        try:
            hook_path = self.hooks_dir / "pre-commit"

            hook_script = """#!/usr/bin/env bash
#
# AI Code Reviewer - Pre-commit Hook
# Automatically reviews code before commit
#

set -e

echo "🤖 Running AI Code Review..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.(py|js|ts|java|go|cpp|c)$' || true)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No code files to review"
    exit 0
fi

# Run code review
python -m src.cli review --files $STAGED_FILES --pre-commit

if [ $? -ne 0 ]; then
    echo "❌ Code review failed. Please fix the issues or use 'git commit --no-verify' to skip."
    exit 1
fi

echo "✅ Code review passed"
exit 0
"""

            # Write hook with executable permissions
            self._write_file_secure(hook_path, hook_script, executable=True)

            logger.info(f"Pre-commit hook installed: {hook_path}")
            return True

        except Exception as e:
            logger.error(f"Error installing pre-commit hook: {e}")
            return False

    def install_commit_msg_hook(self) -> bool:
        """
        Install commit-msg hook for commit message validation.

        Returns:
            bool: True if successful
        """
        if not self.hooks_dir.exists():
            logger.error(f"Git hooks directory not found: {self.hooks_dir}")
            return False

        try:
            hook_path = self.hooks_dir / "commit-msg"

            hook_script = """#!/usr/bin/env bash
#
# AI Code Reviewer - Commit Message Hook
# Validates commit message format
#

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check commit message format (Conventional Commits)
if ! echo "$COMMIT_MSG" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\\(.+\\))?: .{1,}'; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "Please use Conventional Commits format:"
    echo "  feat: add new feature"
    echo "  fix: fix bug"
    echo "  docs: update documentation"
    echo "  style: code style changes"
    echo "  refactor: code refactoring"
    echo "  test: add tests"
    echo "  chore: maintenance tasks"
    echo ""
    exit 1
fi

echo "✅ Commit message format valid"
exit 0
"""

            # Write hook with executable permissions
            self._write_file_secure(hook_path, hook_script, executable=True)

            logger.info(f"Commit-msg hook installed: {hook_path}")
            return True

        except Exception as e:
            logger.error(f"Error installing commit-msg hook: {e}")
            return False

    def uninstall_hooks(self) -> bool:
        """
        Uninstall all hooks.

        Returns:
            bool: True if successful
        """
        try:
            hooks = ["pre-commit", "commit-msg", "pre-push"]
            for hook_name in hooks:
                hook_path = self.hooks_dir / hook_name
                if hook_path.exists():
                    hook_path.unlink()
                    logger.info(f"Removed hook: {hook_name}")

            return True

        except Exception as e:
            logger.error(f"Error uninstalling hooks: {e}")
            return False


class JetBrainsIntegration(IDEIntegration):
    """JetBrains IDEs (PyCharm, IntelliJ, etc.) integration."""

    def __init__(self):
        super().__init__()
        self.plugin_dir = self._get_plugin_dir()

    def _get_plugin_dir(self) -> Optional[Path]:
        """Get JetBrains plugins directory."""
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA")) / "JetBrains"
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "JetBrains"
        else:
            base = Path.home() / ".local" / "share" / "JetBrains"

        return base if base.exists() else None

    def install_plugin(self) -> bool:
        """
        Install JetBrains plugin.

        Returns:
            bool: True if successful
        """
        logger.info("JetBrains plugin installation not yet implemented")
        return False


class SublimeTextIntegration(IDEIntegration):
    """Sublime Text integration."""

    def __init__(self):
        super().__init__()
        self.packages_dir = self._get_packages_dir()

    def _get_packages_dir(self) -> Optional[Path]:
        """Get Sublime Text packages directory."""
        if sys.platform == "win32":
            packages_dir = Path(os.getenv("APPDATA")) / "Sublime Text" / "Packages"
        elif sys.platform == "darwin":
            packages_dir = (
                Path.home() / "Library" / "Application Support" / "Sublime Text" / "Packages"
            )
        else:
            packages_dir = Path.home() / ".config" / "sublime-text" / "Packages"

        return packages_dir if packages_dir.exists() else None

    def install_package(self) -> bool:
        """
        Install Sublime Text package.

        Returns:
            bool: True if successful
        """
        logger.info("Sublime Text package installation not yet implemented")
        return False


# ============================================================================
# Helper Functions
# ============================================================================


def setup_ide_integration(ide: str = "vscode") -> bool:
    """
    Setup IDE integration.

    Args:
        ide: IDE to setup (vscode, pycharm, sublime)

    Returns:
        bool: True if successful
    """
    try:
        if ide.lower() == "vscode":
            integration = VSCodeIntegration()
            return integration.install_extension()
        elif ide.lower() in ["pycharm", "intellij", "jetbrains"]:
            integration = JetBrainsIntegration()
            return integration.install_plugin()
        elif ide.lower() == "sublime":
            integration = SublimeTextIntegration()
            return integration.install_package()
        else:
            logger.error(f"Unsupported IDE: {ide}")
            return False

    except Exception as e:
        logger.error(f"Error setting up IDE integration: {e}")
        return False


def setup_git_hooks(repo_path: Optional[Path] = None) -> bool:
    """
    Setup Git hooks.

    Args:
        repo_path: Path to Git repository

    Returns:
        bool: True if successful
    """
    try:
        integration = GitHooksIntegration(repo_path)
        success = True

        if not integration.install_pre_commit_hook():
            success = False

        if not integration.install_commit_msg_hook():
            success = False

        return success

    except Exception as e:
        logger.error(f"Error setting up Git hooks: {e}")
        return False
