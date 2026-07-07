# s5_skill.py - 领域 Skill 版本
# 功能：在通用规则的基础上，叠加领域专业知识（心理学学习助手）
# 相比 s4：同时加载 agent.md 和 skill.md，让 AI 成为特定领域的专家助手

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 创建 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 【核心差异】加载并拼接多个 prompt 文件
# 1. agent.md：通用规则（怎么输出、怎么执行命令）
# 2. skill.md：领域知识（心理学学习助手的专业能力）
def load_prompt(filename: str) -> str:
    """从 markdown 文件读取 prompt"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

# 加载通用规则
general_prompt = load_prompt("agent.md")
if not general_prompt:
    print("错误：找不到 agent.md 文件")
    sys.exit(1)

# 加载领域知识
skill_prompt = load_prompt("skill.md")
if not skill_prompt:
    print("错误：找不到 skill.md 文件")
    sys.exit(1)

# 【关键】拼接两个 prompt
# 最终的 system prompt = 通用规则 + 领域知识
combined_prompt = f"""{general_prompt}

---

# 领域专业知识

{skill_prompt}"""

messages = [{"role": "system", "content": combined_prompt}]

print("=" * 50)
print("s5_skill.py - 领域 Skill 版本")
print("角色：心理学学习助手")
print("能力：整理笔记、解释概念、生成学习计划")
print("输入 'quit' 或 '退出' 结束程序")
print("=" * 50)

# 外层循环：等待用户输入
while True:
    user_input = input("\n你：")

    if user_input.lower() in ['quit', '退出', 'exit']:
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})

    # 内层循环：Agent 执行
    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})
        print(f"\n[AI] {reply}")

        if reply.strip().startswith("完成:"):
            break

        if "命令:" in reply:
            command = reply.strip().split("命令:")[1].strip()
            print(f"\n[系统] 执行命令: {command}")
            result = os.popen(command).read()
            print(f"[系统] 结果: {result}")
            messages.append({"role": "user", "content": f"执行完毕:{result}"})

# 【与 s4 的区别】
# s4：只加载一个 agent.md，AI 是通用助手
# s5：加载 agent.md + skill.md，AI 成为特定领域专家
#
# 这种架构的好处：
# 1. agent.md 可以复用（比如换成"英语学习助手"，只需换 skill.md）
# 2. 不同领域的 Agent 可以共享同一套通用规则
# 3. 领域专家可以维护 skill.md，程序员维护代码