"""
Tool Orchestration Module
=========================
Harness 的工具调度层 —— 预置 Agent 可用的工具，统一管理调用逻辑。

工具安全分级（与 guard.py 对应）：
  AUTO_APPROVE  : list_files, read_file, get_file_info  ← 纯读
  ALWAYS_CONFIRM: write_file, delete_file               ← 写/删
  KEYWORD_CHECK : run_python                            ← 内容决定风险
"""

import os
import subprocess
from langchain_core.tools import tool

SANDBOX = "/tmp/sandbox"
os.makedirs(SANDBOX, exist_ok=True)


def _safe_path(filename: str) -> str:
    """防止路径穿越攻击，强制限定在沙箱目录内"""
    return os.path.join(SANDBOX, os.path.basename(filename))


# ── AUTO_APPROVE 工具（纯读，无副作用）─────────────────

@tool
def list_files() -> str:
    """List all files currently in the sandbox directory."""
    files = os.listdir(SANDBOX)
    if not files:
        return "📂 Sandbox is empty."
    return "📂 Files in sandbox:\n" + "\n".join(f"  - {f}" for f in sorted(files))


@tool
def read_file(filename: str) -> str:
    """
    Read and return the content of a file in the sandbox.

    Args:
        filename: Name of the file to read
    """
    path = _safe_path(filename)
    if not os.path.exists(path):
        return f"❌ File not found: {filename}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if len(content) > 3000:
        content = content[:3000] + "\n... (truncated)"
    return content


@tool
def get_file_info(filename: str) -> str:
    """
    Return metadata about a file in the sandbox (size, modified time).

    Args:
        filename: Name of the file to inspect
    """
    path = _safe_path(filename)
    if not os.path.exists(path):
        return f"❌ File not found: {filename}"
    stat = os.stat(path)
    import datetime
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"📄 {filename}\n"
        f"   Size    : {stat.st_size} bytes\n"
        f"   Modified: {mtime}"
    )


# ── ALWAYS_CONFIRM 工具（有持久化副作用）───────────────

@tool
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file inside the sandbox directory.

    Args:
        filename: Name of the file (e.g. 'main.py')
        content: Full content to write
    """
    path = _safe_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ File written: {path} ({len(content)} chars)"


@tool
def delete_file(filename: str) -> str:
    """
    Delete a file from the sandbox directory.

    Args:
        filename: Name of the file to delete
    """
    path = _safe_path(filename)
    if not os.path.exists(path):
        return f"❌ File not found: {filename}"
    os.remove(path)
    return f"🗑️  File deleted: {filename}"


# ── KEYWORD_CHECK 工具（内容决定风险）──────────────────

@tool
def run_python(filename: str) -> str:
    """
    Execute a Python file inside the sandbox directory.

    Args:
        filename: Name of the Python file to run
    """
    path = _safe_path(filename)
    if not os.path.exists(path):
        return f"❌ Error: {path} does not exist. Did you write the file first?"
    try:
        result = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=SANDBOX,
        )
        output = result.stdout or result.stderr or "(no output)"
    except subprocess.TimeoutExpired:
        output = "❌ Timeout: execution exceeded 15 seconds and was terminated."

    if len(output) > 2000:
        output = output[:2000] + "\n... (output truncated)"
    return output


# ── 注册表 ──────────────────────────────────────────────
TOOLS = [list_files, read_file, get_file_info, write_file, delete_file, run_python]
