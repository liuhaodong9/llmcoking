# DeepCoke 项目规则

## 项目概述
焦化配煤机器人智能大脑，多 Agent 架构：Coal Agent（配煤优化）+ RAG Agent（文献问答）。
GitHub: liuhaodong9/llmcoking

## 架构
```
FastAPI (test.py:8000) → Pipeline → Router(关键词匹配)
  ├── "optimization" → Coal Agent (coal_agent/agent_runner.py)
  │     └── Ollama /api/chat + Tools: list_coals, optimize_blend, predict_quality
  ├── factual/process → RAG (ChromaDB 6017条 + ESCARGOT)
  └── general_chat → 直接对话
```

## 启动顺序
1. MySQL + Ollama（后台自动运行）
2. 后端：`cd src/LLM_back && python -m uvicorn test:app --host 0.0.0.0 --port 8000`
3. 前端：`$env:Path += ";C:\Program Files\nodejs"` → `npm run serve`

## 关键文件
- `src/LLM_back/deepcoke/coal_agent/` — 配煤 Agent（agent_runner, quality_predictor, blend_optimizer, coal_db）
- `src/LLM_back/deepcoke/pipeline.py` — Pipeline 总调度
- `src/LLM_back/deepcoke/llm_client.py` — Ollama 原生 API 客户端（不用 OpenAI SDK）
- `src/LLM_back/deepcoke/classifier/question_classifier.py` — 关键词优先匹配路由
- `src/LLM_back/test.py` — FastAPI 入口
- `docs/AI_Agent_Infrastructure_Report.md` — 技术架构报告

## 技术约束
- LLM: Qwen3-8B via Ollama，调用用 requests + /api/chat，不用 OpenAI SDK
- ML模型: 8个 sklearn pickle 在 coal_agent/ 目录下，sklearn 1.7.2
- 优化: scipy differential_evolution + LP fallback
- 数据库: MySQL coaldata (root:123456@127.0.0.1:3306)
- ChromaDB: 已有 collection 获取时不传 embedding_function（避免冲突）

## 产品定位
- 软件统一，硬件分版本：沙盘演示版 + 高校教学版
- 配套 ESP32 + MQTT 控制料斗
- 全本地部署，无需联网
