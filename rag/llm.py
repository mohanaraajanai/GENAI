from __future__ import annotations

from langchain_openai import ChatOpenAI


def create_llm(model: str, temperature: float = 0.2):
    """Create the configured OpenAI chat model with LangSmith metadata."""
    kwargs = {
        "model": model,
        "streaming": True,
    }
    try:
        return ChatOpenAI(
            **kwargs,
            temperature=temperature,
        ).with_config(
            tags=["agri-farmer-adviser", "rag-generation"],
            metadata={"application": "vikaspedia-agri-farmer-adviser"},
        )
    except Exception:
        return ChatOpenAI(**kwargs).with_config(
            tags=["agri-farmer-adviser", "rag-generation"],
            metadata={"application": "vikaspedia-agri-farmer-adviser"},
        )
