"""LLM provider abstractions for lane."""

from .base import LLMProvider
from .openai_compat import OpenAICompatProvider

__all__ = ["LLMProvider", "OpenAICompatProvider"]
