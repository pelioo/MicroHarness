"""
Prompt Management Module
========================
Harness 的提示管理层 —— 负责在每次启动时给模型注入正确的"入职手册"。

v2 更新：启动时自动读取长期记忆并注入到系统提示，
         让模型感知上次会话做了什么。
"""

from memory import format_memories_for_prompt, load_memories

SYSTEM_PROMPT_BASE = """
You are a coding assistant operating inside a safe harness.

Rules:
- You may write files and run Python code inside the sandbox
- You MUST NOT run shell commands that delete, move, or overwrite files outside the workspace
- Always explain what you are about to do before doing it
- If a task is unclear, ask for clarification instead of guessing
- Keep code clean, readable, and well-commented

Workspace: /tmp/sandbox/
"""


def get_system_prompt() -> str:
    """
    组装系统提示：基础规则 + 长期记忆（如果有）。

    每次 Agent 启动时调用，自动把上次会话的关键信息追加进来，
    让模型具备跨会话的上下文感知能力。
    """
    base = SYSTEM_PROMPT_BASE.strip()
    memories = load_memories()
    memory_block = format_memories_for_prompt(memories)

    if memory_block:
        full_prompt = f"{base}\n\n{memory_block}"
        print(f"[HARNESS] Memory loaded: {len(memories)} record(s) injected into prompt.")
        return full_prompt

    return base
