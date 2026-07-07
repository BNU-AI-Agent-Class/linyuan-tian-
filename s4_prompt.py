# s4_prompt.py - Prompt 外置版本
# 功能：将 system prompt 从代码中分离到外部文件 agent.md
# 相比 s3：代码更清晰，prompt 更易维护，非程序员也能修改 AI 行为

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

# 【核心差异】从外部文件读取 system prompt
# 好处：
# 1. 代码和配置分离，更易维护
# 2. 非 Python 程序员也能修改 AI 行为
# 3. 同一个 prompt 可以被多个脚本复用
def load_prompt(filename: str) -> str:
    """从 markdown 文件读取 prompt"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：找不到 {filename} 文件")
        print("请确保 agent.md 文件存在")
        sys.exit(1)

# 加载外部 prompt
system_prompt = load_prompt("agent.md")

messages = [{"role": "system", "content": system_prompt}]

print("=" * 50)
print("s4_prompt.py - Prompt 外置版本")
print("System Prompt 从 agent.md 文件读取")
print("输入任务，AI 会自动决定执行什么命令")
print("输入 'quit' 或 '退出' 结束程序")
print("=" * 50)

# 外层循环：等待用户输入新任务
while True:
    user_input = input("\n你：")

    if user_input.lower() in ['quit', '退出', 'exit']:
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})

    # 内层循环：Agent 自主执行
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

# 【与 s3 的区别】
# s3：system prompt 写死在代码里
# s4：system prompt 存在 agent.md 文件中，代码更简洁，prompt 更易修改
#
# 如果你想让 AI 换一种行为风格，只需要修改 agent.md，不用动 Python 代码
