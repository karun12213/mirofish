"""
LLM Client - Unified interface
Supports both OpenAI-format APIs and Anthropic Claude
"""

import json
import re
import os
from typing import Optional, Dict, Any, List

from ..config import Config


class LLMClient:
    """LLM Client - auto-detects Anthropic vs OpenAI based on API key"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")
        
        # Auto-detect: if key starts with sk-ant, use Anthropic SDK
        self.is_anthropic = self.api_key.startswith("sk-ant-")
        
        if self.is_anthropic:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            # Default model if not set
            if not self.model or self.model in ("qwen-plus", "your_model_name_here"):
                self.model = "claude-sonnet-4-20250514"
        else:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Send a chat request
        
        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max tokens
            response_format: Response format (e.g. JSON mode)
            
        Returns:
            Model response text
        """
        if self.is_anthropic:
            return self._chat_anthropic(messages, temperature, max_tokens)
        else:
            return self._chat_openai(messages, temperature, max_tokens, response_format)
    
    def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chat using Anthropic Claude API"""
        # Extract system message if present
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg += msg["content"] + "\n"
            else:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Anthropic requires at least one user message
        if not chat_messages:
            chat_messages = [{"role": "user", "content": "Hello"}]
        
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_messages,
        }
        
        if system_msg.strip():
            kwargs["system"] = system_msg.strip()
        
        response = self.client.messages.create(**kwargs)
        content = response.content[0].text
        # Remove <think> blocks if present
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """Chat using OpenAI-compatible API"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send a chat request and return JSON
        
        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max tokens
            
        Returns:
            Parsed JSON object
        """
        if self.is_anthropic:
            # For Anthropic, add explicit JSON instruction to the last user message
            enhanced_messages = list(messages)
            # Ensure LLM knows to respond in JSON
            if enhanced_messages and enhanced_messages[-1]["role"] == "user":
                enhanced_messages[-1] = {
                    "role": "user",
                    "content": enhanced_messages[-1]["content"] + "\n\nIMPORTANT: Respond ONLY with valid JSON, no markdown code blocks, no explanation."
                }
            response = self.chat(
                messages=enhanced_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            response = self.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
        
        # Clean markdown code block markers
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {cleaned_response[:200]}")
