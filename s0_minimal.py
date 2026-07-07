# s0_minimal.py - 最小 API 骨架
# 功能：只验证 DeepSeek API 环境能否正常工作
# 这是 AI Agent 的"Hello World"版本

from dotenv import load_dotenv
load_dotenv()  # 1. 加载 .env 文件中的环境变量

from openai import OpenAI  # 2. 导入 OpenAI SDK
import os
import sys

# 3. 设置 Windows 终端编码为 UTF-8，避免中文乱码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 4. 创建 DeepSeek 客户端
# 使用 OpenAI SDK，但指向 DeepSeek 的 API 地址
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key
    base_url="https://api.deepseek.com"      # DeepSeek API 地址
)

print("=" * 50)
print("s0_minimal.py - 最小 API 骨架测试")
print("=" * 50)

# 5. 发送一个简单的测试请求
response = client.chat.completions.create(
    model="deepseek-chat",  # DeepSeek 的对话模型
    messages=[
        {"role": "user", "content": "请用一句话介绍你自己"}
    ]
)

# 6. 打印 AI 的回复
print("\n[AI 回复]")
print(response.choices[0].message.content)
print("\n" + "=" * 50)
print("✅ 环境测试成功！API 连接正常。")
print("=" * 50)
