"""
Shared DeepSeek LLM client used across all DeepCoke modules.
"""
from openai import OpenAI
from . import config

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Return a singleton OpenAI-compatible client for DeepSeek."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    return _client


def chat(messages: list[dict], stream: bool = False, **kwargs):
    """Convenience wrapper around chat completions."""
    return get_client().chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=messages,
        stream=stream,
        **kwargs,
    )


def chat_json(messages: list[dict], **kwargs) -> str:
    """Non-streaming call that returns the assistant content string."""
    resp = chat(messages, stream=False, **kwargs)
    return resp.choices[0].message.content.strip()
