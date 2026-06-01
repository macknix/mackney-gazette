"""
LLM interface for the Mackney Gazette.
Drop-in replacement for the original OpenAI module — same function signatures,
now backed by LiteLLM so any model (Gemini, OpenAI, etc.) can be swapped via
the LITELLM_MODEL env var.
"""
import os
import litellm
from typing import List, Dict, Any, Optional

DEFAULT_MODEL = os.environ.get('LITELLM_MODEL', 'gemini/gemini-2.0-flash')

litellm.suppress_debug_info = True


def load_api_key(credentials_file=None) -> str:
    for var in ('GEMINI_API_KEY', 'OPENAI_API_KEY'):
        val = os.environ.get(var)
        if val:
            return val
    raise KeyError("No API key found. Set GEMINI_API_KEY environment variable.")


def call_openai_api(
    system_prompt: str,
    messages: List[Dict[str, str]],
    model_args: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> str:
    if model_args is None:
        model_args = {
            'model': DEFAULT_MODEL,
            'temperature': 0.7,
            'max_tokens': 1024,
            'top_p': 0.95,
        }

    args = model_args.copy()
    model_name  = args.pop('model', DEFAULT_MODEL)
    temperature = args.pop('temperature', 0.7)
    max_tokens  = args.pop('max_tokens', 1024)
    top_p       = args.pop('top_p', 0.95)

    chat_messages = []
    if system_prompt:
        chat_messages.append({"role": "system", "content": system_prompt})

    for msg in messages:
        role = msg.get('role', 'user').lower()
        if role not in ('user', 'assistant', 'system'):
            role = 'user'
        chat_messages.append({"role": role, "content": msg.get('content', '')})

    if not any(m['role'] != 'system' for m in chat_messages):
        chat_messages.append({"role": "user", "content": "Hello"})

    kwargs: Dict[str, Any] = dict(
        model=model_name,
        messages=chat_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        **args,
    )
    if api_key:
        kwargs['api_key'] = api_key

    response = litellm.completion(**kwargs)
    return response.choices[0].message.content


def simple_openai_prompt(
    prompt: str,
    system_instruction: str = "You are a helpful AI assistant.",
    model_args: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> str:
    return call_openai_api(system_instruction, [{'role': 'user', 'content': prompt}], model_args, api_key)
