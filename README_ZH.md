# MicroHarness

[English](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/jingw2/microharness?style=social)](https://github.com/jingw2/microharness)

基于 LangGraph 的最小可运行 Agent Harness demo，支持多模型 Provider。

## 功能特性

- 多 Provider 支持（9 个：Anthropic、OpenAI、DeepSeek、Kimi、Qwen、GLM、MiniMax、Xiaomi、自定义）
- 三级工具安全守卫（自动放行 / 强制确认 / 关键词检测）
- 跨会话长期记忆（持久化到 `memory.json`）
- 最小六层架构（约 500 行代码）

## 快速开始

```bash
# 1. 安装核心依赖
pip install -r requirements.txt

# 如果使用非 Anthropic provider，额外安装：
pip install langchain-openai

# 2. 编辑 .env，填入 Provider 和 API Key
# 3. 运行
python harness.py
```

## 使用示例

### 示例 1：编写并运行 Python 脚本

```
Task: Write a Python script that prints Fibonacci numbers up to 100, then run it

[HARNESS] Step 1/10 — Agent thinking...
[HARNESS] Step 2/10 — Agent thinking...
=======================================================
  FINAL RESPONSE
=======================================================
I wrote fib.py and ran it. Output: 1 1 2 3 5 8 13 21 34 55 89
=======================================================
  Total steps used: 2/10
=======================================================
[HARNESS] Memory saved: User asked to write and run a Fibonacci script.
```

### 示例 2：跨会话使用长期记忆

第二次启动时，Harness 自动加载上次会话摘要：

```
[HARNESS] Found 1 long-term memory record(s).
          Last: 2024-01-15 — User asked to write and run a Fibonacci script...

Task: Improve the script from last time

[HARNESS] Step 1/10 — Agent thinking...
(Agent recalls previous session context from injected memory)
```

### 示例 3：安全守卫拦截危险操作

当 Agent 尝试执行高危代码时，守卫会暂停并请求人工确认：

```
[HARNESS] Step 2/10 — Agent thinking...

=======================================================
  [HARNESS GUARD] ⚠️  HIGH RISK
  Tool   : run_python
  code    : import shutil; shutil.rmtree('/tmp/sandbox')
=======================================================
  Approve? (yes / no): no
  ❌ Rejected. Operation cancelled.
```

## Provider 配置

编辑 `.env` 文件，选择 Provider 并填入对应的 Key：

### Anthropic（默认）
```bash
PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
MAIN_MODEL=claude-sonnet-4-20250514
MEMORY_MODEL=claude-haiku-4-5-20251001
```

### DeepSeek
```bash
PROVIDER=deepseek
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=deepseek-chat
MEMORY_MODEL=deepseek-chat
```

### Kimi（Moonshot）
```bash
PROVIDER=kimi
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=moonshot-v1-8k
MEMORY_MODEL=moonshot-v1-8k
```

### Qwen（通义千问）
```bash
PROVIDER=qwen
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=qwen-plus
MEMORY_MODEL=qwen-turbo
```

### GLM（智谱）
```bash
PROVIDER=glm
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=glm-4-air
MEMORY_MODEL=glm-4-flash
```

### MiniMax
```bash
PROVIDER=minimax
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=abab6.5s-chat
MEMORY_MODEL=abab6.5s-chat
```

### OpenAI / GPT
```bash
PROVIDER=openai
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=gpt-4o
MEMORY_MODEL=gpt-4o-mini
```

### Xiaomi（小米）
```bash
PROVIDER=xiaomi
OPENAI_COMPATIBLE_API_KEY=your_key
MAIN_MODEL=your-model-name
MEMORY_MODEL=your-model-name
```

### 自定义 Provider（任何 OpenAI 兼容接口）
```bash
PROVIDER=custom
OPENAI_COMPATIBLE_API_KEY=your_key
OPENAI_COMPATIBLE_BASE_URL=https://your-api-endpoint/v1
MAIN_MODEL=your-model-name
MEMORY_MODEL=your-model-name
```

## 工具安全分级

| 工具 | 级别 | 行为 |
|---|---|---|
| `list_files` | AUTO_APPROVE | 自动放行 |
| `read_file` | AUTO_APPROVE | 自动放行 |
| `get_file_info` | AUTO_APPROVE | 自动放行 |
| `write_file` | ALWAYS_CONFIRM | 强制人工确认 |
| `delete_file` | ALWAYS_CONFIRM | 强制人工确认 |
| `run_python` | KEYWORD_CHECK | 含危险关键词时拦截 |

## 六层架构

| 层 | 文件 | 职责 |
|---|---|---|
| 配置管理 | `config.py` | 读取 .env，按 provider 构建 LLM 实例 |
| 提示管理 | `prompts.py` | 系统提示 + 长期记忆注入 |
| 工具调度 | `tools.py` | 6 个工具，沙箱隔离（/tmp/sandbox/） |
| 安全守卫 | `guard.py` | 三级分类，人工确认 |
| 生命周期 | `harness.py` | MAX_STEPS，路由控制 |
| 长期记忆 | `memory.py` | 跨会话持久化，memory.json |

## License

本项目基于 [MIT License](LICENSE) 开源。转载或分享本项目及其内容时，请注明出处：[jingw2/microharness](https://github.com/jingw2/microharness)。

## Star 走势

[![Star History Chart](https://api.star-history.com/svg?repos=jingw2/microharness&type=Date)](https://star-history.com/#jingw2/microharness&Date)
