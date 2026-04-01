# DeepCoke 智能焦化决策平台

基于多 Agent 架构的焦化配煤智能问答系统，集成配煤优化、文献检索、知识图谱与语音对话功能。

## 系统架构

```
┌─────────────────────────────────────────────┐
│           Vue 2 前端 (port 8080)             │
│   LoginPage → LandingPage → HomePage        │
│   ├── MainDia (文本对话)                     │
│   └── VoiceAgent (语音对话)                  │
└──────┬───────────────────────────┬───────────┘
       │ HTTP                      │ WebSocket
┌──────▼──────────────┐    ┌──────▼──────────────┐
│ 文本后端 (port 8000) │    │ 语音后端 (port 8001) │
│ FastAPI + Pipeline   │    │ FastAPI + WebSocket  │
│ ├── Coal Agent       │    │ ├── ASR (Whisper)    │
│ ├── RAG (ChromaDB)   │    │ ├── TTS              │
│ └── Knowledge Graph  │    │ └── DeepSeek LLM     │
└──────────────────────┘    └──────────────────────┘
```

## 环境要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | >= 3.10 | 后端运行 |
| Node.js | >= 14 | 前端构建 |
| MySQL | 8.0 | 会话存储 |
| Ollama | latest | 本地 LLM (Qwen3-8B) |

## 快速开始

### 1. 安装依赖

```bash
# 前端依赖
npm install

# 文本后端依赖
pip install -r src/LLM_back/deepcoke/requirements.txt

# 语音后端依赖
cd voice_agent_backend
pip install -e .
```

### 2. 配置

**MySQL 数据库**（首次运行自动建表）：
- 地址：`127.0.0.1:3306`
- 数据库名：`chat_db`（需手动创建）
- 账号：`root` / 密码：`123456`

```sql
CREATE DATABASE IF NOT EXISTS chat_db DEFAULT CHARACTER SET utf8mb4;
```

**Ollama 模型**：
```bash
ollama pull qwen3:8b
```

**语音后端**（可选）：
```bash
# 复制并编辑环境变量
cp voice_agent_backend/.env.example voice_agent_backend/.env
# 至少配置 DEEPSEEK_API_KEY
```

### 3. 启动服务

#### 方式一：一键启动（推荐）

双击 `start_all_windows.bat`

#### 方式二：手动启动（3 个终端）

**终端 1 - 文本后端 (port 8000)**：
```bash
cd src/LLM_back
python -m uvicorn test:app --host 0.0.0.0 --port 8000
```

**终端 2 - 语音后端 (port 8001)**：
```bash
cd voice_agent_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**终端 3 - 前端 (port 8080)**：
```bash
npm run serve
```

> Windows 下如 Node.js 未加入 PATH，先执行：`$env:Path += ";C:\Program Files\nodejs"`

### 4. 访问

- 前端界面：http://localhost:8080
- 文本 API：http://localhost:8000/docs
- 语音健康检查：http://localhost:8001/health

## 项目结构

```
llmcoking/
├── src/
│   ├── components/              # Vue 前端组件
│   │   ├── LoginPage.vue        # 登录页
│   │   ├── LandingPage.vue      # 产品首页
│   │   ├── HomePage.vue         # 主布局（侧边栏 + 路由）
│   │   ├── MainDia.vue          # 文本对话界面
│   │   └── VoiceAgent.vue       # 语音对话界面
│   │
│   └── LLM_back/                # 文本后端
│       ├── test.py              # FastAPI 入口 (port 8000)
│       └── deepcoke/
│           ├── pipeline.py      # 问答管道总调度
│           ├── llm_client.py    # Ollama 原生 API 客户端
│           ├── classifier/      # 问题分类路由
│           ├── coal_agent/      # 配煤优化 Agent + 8个ML模型
│           ├── vectorstore/     # ChromaDB RAG 检索
│           ├── generation/      # 流式答案生成
│           ├── reasoning/       # ESCARGOT 推理引擎
│           └── knowledge_graph/ # Neo4j 知识图谱
│
├── voice_agent_backend/         # 语音后端 (port 8001)
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── routers/             # WebSocket 路由
│   │   └── services/            # ASR/TTS/VAD 服务
│   └── pyproject.toml
│
├── glossary/                    # 焦化专业术语库
├── docs/                        # 项目文档
├── start_all_windows.bat        # 一键启动脚本
└── package.json                 # 前端配置
```

## 核心功能

| 功能 | 入口关键词 | 说明 |
|------|-----------|------|
| 智能配煤 | "优化""配煤""blend" | Coal Agent 调用 ML 模型预测质量 + scipy 优化配比 |
| 文献问答 | 焦化工艺相关问题 | RAG 从 6017 条文献中检索 + ESCARGOT 推理 |
| 通用对话 | 其他问题 | Qwen3-8B 直接回答 |
| 语音对话 | 前端语音按钮 | 全双工 WebSocket + Whisper ASR |

## 技术栈

- **前端**：Vue 2 + Element UI + Markdown-it + KaTeX + Highlight.js
- **文本后端**：FastAPI + SQLAlchemy + ChromaDB + scikit-learn + scipy
- **语音后端**：FastAPI + WebSocket + Whisper + Edge TTS
- **LLM**：Qwen3-8B (Ollama) / DeepSeek API
- **数据库**：MySQL 8.0 + ChromaDB + Neo4j (可选)

## 许可

MIT License
