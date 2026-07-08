#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极版 mini Claude Code - DeepSeek 版本

整合 c0-c5 所有功能 + 强力扩展
使用 DeepSeek API（兼容 OpenAI 格式）
"""
import os
import json
import glob as glob_module
from datetime import datetime
from openai import OpenAI

# ============ 配置 ============
MODEL = "deepseek-chat"
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # 从环境变量读取，请设置 DEEPSEEK_API_KEY
BASE_URL = "https://api.deepseek.com/v1"

LIMIT = 20          # 历史条数阈值
MAX_RETRY = 5       # 最大重试次数
DANGER_CMDS = ["rm ", "rmdir", "del ", "sudo", "mv ", "> /", "mkfs", "dd ", "format", "shutdown", "reboot"]

# ============ 全局状态 ============
TODOS = []
HISTORY_LOG = []
client = None

# ============ 工具函数 ============

def read_file(path):
    """读取文件内容"""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：文件 '{path}' 不存在"
    except Exception as e:
        return f"错误：无法读取文件 '{path}' - {str(e)}"

def write_file(path, text):
    """写入文件"""
    try:
        if os.path.exists(path):
            backup = read_file(path)
            HISTORY_LOG.append({"action": "write", "path": path, "backup": backup, "time": datetime.now().isoformat()})
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return f"已写入 {path}（{len(text)} 字符）"
    except Exception as e:
        return f"错误：无法写入文件 '{path}' - {str(e)}"

def edit_file(path, old_text, new_text):
    """精确编辑文件"""
    try:
        content = read_file(path)
        if old_text not in content:
            return f"错误：在文件中未找到目标文本"
        HISTORY_LOG.append({"action": "edit", "path": path, "backup": content, "old": old_text, "time": datetime.now().isoformat()})
        new_content = content.replace(old_text, new_text, 1)
        write_file(path, new_content)
        return f"已编辑 {path}，替换了 {len(old_text)} 字符"
    except Exception as e:
        return f"错误：编辑失败 - {str(e)}"

def bash(cmd):
    """执行 shell 命令 + 权限门"""
    if any(d in cmd for d in DANGER_CMDS):
        ans = input(f"[权限门] 要执行危险命令：{cmd}\n允许吗？(y/n) ").strip().lower()
        if ans != "y":
            return "用户拒绝了这条命令"
    try:
        result = os.popen(cmd).read()
        HISTORY_LOG.append({"action": "bash", "cmd": cmd, "result": result, "time": datetime.now().isoformat()})
        return result if result else "(无输出)"
    except Exception as e:
        return f"执行错误：{str(e)}"

def search(keyword, path="."):
    """搜索工具（作业选项A）- 在项目中搜索关键词"""
    results = []
    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            for file in files:
                filepath = os.path.join(root, file)
                if not file.endswith(('.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.sh')):
                    continue
                try:
                    with open(filepath, encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if keyword in line:
                                results.append(f"{filepath}:{i}: {line.strip()[:80]}")
                                if len(results) >= 30:
                                    return f"找到 {len(results)} 处匹配（已截断）：\n" + "\n".join(results)
                except (UnicodeDecodeError, PermissionError):
                    continue
        if results:
            return f"找到 {len(results)} 处匹配：\n" + "\n".join(results)
        return f"未找到关键词 '{keyword}'"
    except Exception as e:
        return f"搜索错误：{str(e)}"

def glob_files(pattern, path="."):
    """文件匹配工具"""
    try:
        matches = glob_module.glob(os.path.join(path, pattern), recursive=True)
        matches = [m for m in matches if '.git' not in m and '__pycache__' not in m]
        if matches:
            return "\n".join(matches[:50])
        return f"未找到匹配 '{pattern}' 的文件"
    except Exception as e:
        return f"Glob 错误：{str(e)}"

def todo_write(items):
    """计划工具（作业选项C2 - TodoWrite）"""
    global TODOS
    TODOS = items
    board = "\n".join(f"  {'[x]' if t['done'] else '[ ]'} {t['task']}" for t in TODOS)
    print(f"\n[计划板]\n{board}\n")
    return "清单已更新"

def undo_last():
    """撤销上一次文件操作"""
    if not HISTORY_LOG:
        return "没有可撤销的操作"
    last = HISTORY_LOG.pop()
    if last["action"] in ["write", "edit"]:
        write_file(last["path"], last["backup"])
        return f"已撤销 {last['path']} 的修改"
    return "无法撤销此类型操作"

def call_model(messages):
    """调用 DeepSeek API"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def subagent(task, agent_type="general"):
    """子智能体工具（作业选项B）"""
    sub_messages = []

    if agent_type == "code_reviewer":
        sub_messages.append({
            "role": "system",
            "content": """你是代码审查员。你的任务是阅读代码、找出潜在 bug 和逻辑漏洞。
重点关注：
- 空输入/边界情况导致的崩溃（如 IndexError, KeyError）
- 异常未处理
- 逻辑错误
- 安全漏洞

用 JSON 格式回复：
{"tool": "read_file", "args": {"path": "..."}} 或 {"done": "bug报告：..."}
只报告问题，不修改代码。"""
        })
    else:
        sub_messages.append({
            "role": "system",
            "content": """你是子助手，用 JSON 格式工作：
{"tool": "bash", "args": {"cmd": "..."}} 或 {"done": "结论"}
只返回最终结论，不要把过程细节全返回。"""
        })

    sub_messages.append({"role": "user", "content": task})

    retry_count = 0
    while retry_count < MAX_RETRY:
        r = call_model(sub_messages)
        sub_messages.append({"role": "assistant", "content": r})

        try:
            a = parse(r)
        except:
            sub_messages.append({"role": "user", "content": "请只回合法 JSON"})
            retry_count += 1
            continue

        if "done" in a:
            return a["done"]

        name, args = a.get("tool"), a.get("args", {})
        if name not in SUB_TOOLS:
            sub_messages.append({"role": "user", "content": f"未知工具 '{name}'，可用工具：{list(SUB_TOOLS.keys())}"})
            retry_count += 1
            continue

        result = SUB_TOOLS[name](**args)
        sub_messages.append({"role": "user", "content": f"输出：\n{result}"})
        retry_count = 0

    return "子 agent 超过最大重试次数，任务失败"

def compact(messages):
    """上下文压缩（作业选项C4）"""
    system = messages[0]
    body = "\n".join(f'{m["role"]}: {m["content"][:200]}...' if len(m["content"]) > 200 else f'{m["role"]}: {m["content"]}' for m in messages[1:])

    summary = call_model([
        {"role": "user", "content": f"""用要点总结这段对话的进展和关键结论：
1. 完成了什么任务
2. 创建/修改了什么文件
3. 还有什么待做
4. 关键发现或问题

对话内容：
{body}"""
        }
    ])

    print("\n[压缩] 历史已折叠成摘要，上下文窗口重开\n")
    return [system, {"role": "user", "content": f"【之前进展摘要】\n{summary}"}]

# ============ 工具注册 ============
TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "bash": bash,
    "search": search,
    "glob": glob_files,
    "todo_write": todo_write,
    "subagent": subagent,
    "undo": undo_last,
}

SUB_TOOLS = {
    "read_file": read_file,
    "bash": bash,
    "search": search,
    "glob": glob_files,
}

# ============ 解析与错误处理 ============
def parse(s):
    """容错解析 JSON"""
    s = s.strip()
    s = s.strip("`").removeprefix("json").strip()
    start = s.find("{")
    end = s.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("未找到 JSON 对象")
    return json.loads(s[start:end])

# ============ 系统提示词 ============
SYSTEM = """你是一个强大的编程助手（mini Claude Code）。每次只回复一个 JSON，不要别的文字，不要 markdown 包裹。

## 可用工具：
- read_file(path) - 读取文件
- write_file(path, text) - 写入文件
- edit_file(path, old_text, new_text) - 精确替换文件中的文本
- bash(cmd) - 执行 shell 命令（危险命令会先问用户）
- search(keyword, path) - 在项目中搜索关键词，返回文件名+行号
- glob(pattern, path) - 匹配文件（如 **/*.py）
- todo_write(items) - 更新任务清单（items 是 [{"task": "...", "done": false/true}]）
- subagent(task, agent_type) - 派子 agent 干活，agent_type 可选 general 或 code_reviewer
- undo() - 撤销上一次文件修改

## 使用原则：
1. 多步任务先用 todo_write 列计划，边做边勾选
2. 探索性脏活交给 subagent（如"读懂整个项目架构"、"审查代码找bug"），保持主对话干净
3. 优先用专用工具而非 bash：read_file/write_file/edit_file 比 cat/echo/sed 更可控
4. 用 search 定位代码：找"哪个文件调用了 X"用 search
5. 代码审查用 code_reviewer：派 subagent(task, "code_reviewer") 去找 bug

## JSON 格式示例：
{"tool": "read_file", "args": {"path": "demo.py"}}
{"tool": "search", "args": {"keyword": "add_note", "path": "."}}
{"tool": "subagent", "args": {"task": "审查代码质量", "agent_type": "code_reviewer"}}
{"tool": "todo_write", "args": {"items": [{"task": "步骤A", "done": false}, {"task": "步骤B", "done": true}]}}
{"done": "总结给用户"}
"""

# ============ 主循环 ============
def main():
    global client
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages = [{"role": "system", "content": SYSTEM}]
    retry_count = 0

    print("=" * 60)
    print("[启动] 终极版 mini Claude Code 已启动 (DeepSeek 版)")
    print("=" * 60)
    print("整合功能：JSON协议 | 工具箱 | 计划 | 子agent | 压缩 | 权限门")
    print("新增功能：搜索 | 代码审查员 | 精确编辑 | 撤销 | 错误处理加强")
    print("=" * 60)
    print("输入任务开始，按 Ctrl+C 退出\n")

    while True:
        try:
            user_input = input("\n你：")
            messages.append({"role": "user", "content": user_input})

            while True:
                # 压缩检查
                if len(messages) > LIMIT:
                    messages = compact(messages)

                # 调用模型
                reply = call_model(messages)
                messages.append({"role": "assistant", "content": reply})

                # 解析 + 错误处理加强版（作业选项C）
                try:
                    action = parse(reply)
                except Exception as e:
                    retry_count += 1
                    if retry_count >= MAX_RETRY:
                        print(f"\n[错误] 连续 {MAX_RETRY} 次解析失败，放弃当前任务")
                        messages.append({"role": "user", "content": "任务已终止，请重新描述你的需求"})
                        retry_count = 0
                        break
                    messages.append({"role": "user", "content": f"上一条不是合法 JSON（错误：{str(e)}）。请只回一个 JSON 对象"})
                    continue

                # 完成？
                if "done" in action:
                    print(f"\n[完成] {action['done']}\n")
                    retry_count = 0
                    break

                # 取出工具和参数
                name = action.get("tool")
                args = action.get("args", {})

                # 作业选项C：未知工具处理
                if name not in TOOLS:
                    retry_count += 1
                    if retry_count >= MAX_RETRY:
                        print(f"\n[错误] 连续 {MAX_RETRY} 次调用未知工具，放弃当前任务")
                        messages.append({"role": "user", "content": "任务已终止"})
                        retry_count = 0
                        break
                    available = list(TOOLS.keys())
                    messages.append({"role": "user", "content": f"没有叫 '{name}' 的工具。可用工具：{available}"})
                    continue

                # 执行工具
                if name != "todo_write":
                    print(f"\n[调用] {name}({args})")

                try:
                    result = TOOLS[name](**args)
                except Exception as e:
                    result = f"工具执行错误：{str(e)}"
                    retry_count += 1

                if name != "todo_write":
                    print(f"[结果] {result[:200]}{'...' if len(result) > 200 else ''}")

                messages.append({"role": "user", "content": f"工具返回：\n{result}"})
                retry_count = 0  # 成功后清零

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n[系统错误] {str(e)}")
            continue

if __name__ == "__main__":
    main()

# MIT License | 郑先隽，北师大心理学部教授，人本AI设计与创新
# 终极版扩展 by Claude Code | DeepSeek 版本适配