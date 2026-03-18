# llmcoking (Merged)

This folder now contains:

- `llmcoking` text chat website (Vue2 + FastAPI, port `8000`)
- `voice-agent` as a voice dialog module (FastAPI websocket backend, port `8001`)

Both are integrated into one frontend site:

- text chat route: `#/Home/MainDia/:sessionId`
- voice chat route: `#/Home/VoiceAgent`

## Quick Start (Windows)

1. Start text backend:
```bat
start_text_backend_windows.bat
```

2. Start voice backend:
```bat
start_voice_backend_windows.bat
```

3. Start frontend:
```bat
start_frontend_windows.bat
```

Then open:

- Frontend: `http://localhost:8080`
- Voice backend health: `http://localhost:8001/health`

You can also use one-click launcher:

```bat
start_all_windows.bat
```

## Voice Backend Config

Edit:

`voice_agent_backend/.env`

At least set:

```ini
DEEPSEEK_API_KEY=your_real_key
```

Recommended:

```ini
WHISPER_LANGUAGE=zh
ASR_SCRIPT_TARGET=simplified
ENABLE_SERVER_TTS=false
```
