# s2_memory.py - 多轮对话 + 记忆
# 功能：AI 能记住之前的对话内容，实现连贯的多轮对话
# 相比 s1：新增 messages 列表存储对话历史，每次请求都带上全部历史

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

print("=" * 50)
print("s2_memory.py - 多轮对话 + 记忆")
print("输入 'quit' 或 '退出' 结束程序")
print("=" * 50)

# 【核心差异】创建消息列表存储对话历史
# 这是 Agent 具备"记忆"的关键
messages = []

# 主循环：多轮对话
while True:
    # 1. 获取用户输入
    user_input = input("\n你：")

    if user_input.lower() in ['quit', '退出', 'exit']:
        print("再见！")
        break

    # 2. 将用户消息添加到历史记录
    messages.append({"role": "user", "content": user_input})

    # 3. 发送请求（带上全部对话历史）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages  # 发送完整的对话历史，而不是只发送当前消息
    )

    # 4. 获取 AI 回复
    ai_reply = response.choices[0].message.content

    # 5. 将 AI 回复也添加到历史记录（形成完整的对话链条）
    messages.append({"role": "assistant", "content": ai_reply})

    # 6. 打印 AI 回复
    print(f"\nAI：{ai_reply}")

# 【与 s1 的区别】
# s1：每次只发送当前消息，AI 没有上下文
# s2：维护 messages 列表，每次发送完整历史，AI 能记住之前说过的话
#
# 示例对话：
# 用户：我叫小明
# AI：你好小明！
# 用户：我叫什么名字？  ← s1 不知道，s2 能回答"小明"
