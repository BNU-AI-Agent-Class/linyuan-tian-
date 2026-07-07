# s3_agent.py - Agent 版本：能执行命令的智能助手
# 功能：AI 不仅能对话，还能决定执行系统命令，形成"感知-决策-行动"闭环
# 相比 s2：新增 system prompt 定义输出格式，AI 可以选择"执行命令"或"完成任务"

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

# 【核心差异】system prompt：定义 AI 的行为规则和输出格式
# 这是 Agent 能"自主决策"的关键
messages = [{
    "role": "system",
    "content": """你必须用以下两种格式之一回复：
- 需要执行命令：命令:XXX（纯命令，不要解释，每次一条）
- 任务完成时：完成:XXX（总结信息）

示例：
用户：创建一个 test 文件夹
AI：命令:mkdir test

用户：看看当前目录有什么
AI：命令:ls

用户：任务完成了
AI：完成:已按要求完成所有操作"""
}]

print("=" * 50)
print("s3_agent.py - Agent 版本（能执行命令）")
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

    # 内层循环：Agent 自主执行，直到任务完成
    while True:
        # 1. AI 决策下一步做什么
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        reply = response.choices[0].message.content

        # 2. 记录 AI 的决策
        messages.append({"role": "assistant", "content": reply})
        print(f"\n[AI] {reply}")

        # 3. 检查是否任务完成
        if reply.strip().startswith("完成:"):
            break

        # 4. 提取并执行命令
        if "命令:" in reply:
            command = reply.strip().split("命令:")[1].strip()
            print(f"\n[系统] 执行命令: {command}")

            # 执行命令并获取结果
            result = os.popen(command).read()
            print(f"[系统] 结果: {result}")

            # 5. 把执行结果反馈给 AI（形成闭环）
            messages.append({"role": "user", "content": f"执行完毕:{result}"})

# 【与 s2 的区别】
# s2：纯对话，AI 只能"说"
# s3：Agent 能"行动"，根据用户意图自动执行命令，形成感知-决策-行动循环
#
# 示例：
# 用户：创建一个 demo 文件夹并在里面创建 hello.txt
# AI：命令:mkdir demo
# 系统：执行完毕
# AI：命令:echo hello > demo/hello.txt
# 系统：执行完毕
# AI：完成:已创建 demo 文件夹和 hello.txt 文件
