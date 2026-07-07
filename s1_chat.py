# s1_chat.py - 单轮对话
# 功能：用户输入一次，AI 回复一次（无记忆）
# 相比 s0：从"固定消息"变成"用户输入"，实现最简单的交互

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
print("s1_chat.py - 单轮对话")
print("输入 'quit' 或 '退出' 结束程序")
print("=" * 50)

# 主循环：每次都是独立的单轮对话
while True:
    # 1. 获取用户输入
    user_input = input("\n你：")

    # 2. 检查是否退出
    if user_input.lower() in ['quit', '退出', 'exit']:
        print("再见！")
        break

    # 3. 发送请求给 AI（注意：每次只发送当前消息，没有历史记录）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": user_input}  # 只发送当前用户消息
        ]
    )

    # 4. 打印 AI 回复
    print(f"\nAI：{response.choices[0].message.content}")

# 【与 s0 的区别】
# s0：固定消息，运行一次就结束
# s1：用户可以输入，可以多次对话，但每次都是独立的（AI 记不住之前说过什么）
