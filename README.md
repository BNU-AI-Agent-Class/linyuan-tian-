# AI Agent 课程作业

北师大郑先隽老师的 AI Agent 课程作业 - 从最小骨架到领域专家助手的递进式学习。

## 项目简介

本项目通过 6 个递进版本的 Python 文件，逐步展示 AI Agent 的核心概念和实现方法。每个版本都在前一个版本的基础上增加新功能，最终实现一个具备专业领域知识的智能助手。

## 版本递进关系

| 版本 | 文件 | 功能 | 核心知识点 |
|------|------|------|------------|
| s0 | `s0_minimal.py` | 最小 API 骨架 | API 连接、环境配置 |
| s1 | `s1_chat.py` | 单轮对话 | 用户输入、基本交互 |
| s2 | `s2_memory.py` | 多轮对话 + 记忆 | 消息历史、上下文理解 |
| s3 | `s3_agent.py` | Agent（命令执行） | System Prompt、感知-决策-行动 |
| s4 | `s4_prompt.py` | Prompt 外置 | 配置分离、可维护性 |
| s5 | `s5_skill.py` | 领域 Skill | Prompt 拼接、领域专家 |

### 版本详细说明

#### s0_minimal.py - 最小骨架
- 只验证 DeepSeek API 能否正常工作
- 发送固定消息，获取 AI 回复
- **学习要点**：API 连接、环境变量配置

#### s1_chat.py - 单轮对话
- 用户可以输入问题，AI 回复
- 每次对话独立，AI 不记住了之前的内容
- **学习要点**：用户输入处理、基本交互循环

#### s2_memory.py - 多轮对话 + 记忆
- 维护消息历史列表 `messages`
- AI 能记住之前说过的话
- **学习要点**：对话记忆、上下文传递

#### s3_agent.py - Agent 版本
- AI 能决定执行系统命令
- 形成"用户需求 → AI 决策 → 命令执行 → 结果反馈"闭环
- **学习要点**：System Prompt、输出格式约束、命令执行

#### s4_prompt.py - Prompt 外置
- System Prompt 从代码分离到 `agent.md` 文件
- 非程序员也能修改 AI 行为
- **学习要点**：配置分离、文件读取

#### s5_skill.py - 领域 Skill
- 同时加载 `agent.md`（通用规则）和 `skill.md`（领域知识）
- 实现心理学学习助手
- **学习要点**：Prompt 拼接、领域专家构建

## 环境配置

### 1. 克隆仓库

```bash
git clone https://github.com/a pig/BNU-AI-Agent-Class.git
cd BNU-AI-Agent-Class
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key

```bash
# 复制模板文件
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=sk-your-api-key-here
```

获取 DeepSeek API Key：https://platform.deepseek.com/

## 运行方法

每个文件都可以独立运行：

```bash
# s0 - 测试 API 连接
python s0_minimal.py

# s1 - 单轮对话
python s1_chat.py

# s2 - 多轮对话（AI 有记忆）
python s2_memory.py

# s3 - Agent 版本（能执行命令）
python s3_agent.py

# s4 - Prompt 外置版本
python s4_prompt.py

# s5 - 心理学学习助手
python s5_skill.py
```

## 文件结构

```
├── s0_minimal.py       # 最小骨架
├── s1_chat.py          # 单轮对话
├── s2_memory.py        # 多轮对话 + 记忆
├── s3_agent.py         # Agent 版本
├── s4_prompt.py        # Prompt 外置
├── s5_skill.py         # 领域 Skill
├── agent.md            # 通用规则 prompt
├── skill.md            # 心理学助手领域知识
├── .env.example        # API Key 模板
├── .env                # 实际 API Key（不上传）
├── .gitignore          # Git 忽略配置
├── requirements.txt    # Python 依赖
└── README.md           # 项目说明
```

## 技术栈

- **API**: DeepSeek API（兼容 OpenAI SDK）
- **模型**: deepseek-chat
- **语言**: Python 3.8+

## 注意事项

- `.env` 文件包含敏感信息，已通过 `.gitignore` 排除，请勿上传到 GitHub
- 所有代码使用 DeepSeek API，需要有效的 API Key
- Windows 用户可能需要配置 UTF-8 编码以正确显示中文

## 作者

北师大心理学部 AI Agent 课程作业
