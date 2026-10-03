from __future__ import annotations
import json, os
from anthropic import Anthropic
from .memory import get_history, save_message
from .system_prompt import SYSTEM_PROMPT
from tools import TOOL_SCHEMAS, DISPATCH

class Agent:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self.chat_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if os.getenv("GEMINI_API_KEY"):
            self.chat_base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
            self.chat_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        elif os.getenv("GROQ_API_KEY"):
            self.chat_base = "https://api.groq.com/openai/v1"
            self.chat_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        elif os.getenv("OPENAI_API_KEY"):
            self.chat_base = "https://api.openai.com/v1"
            self.chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            self.chat_base = None
            self.chat_model = None

    def chat(self, session_id: str, message: str) -> dict:
        history = get_history(session_id)
        if not self.client and not self.chat_key:
            text = "compAI est démarré, mais aucune clé d'IA n'est configurée. Ajoutez GEMINI_API_KEY ou ANTHROPIC_API_KEY pour activer l'agent."
            save_message(session_id, "user", message); save_message(session_id, "assistant", text)
            return {"session_id": session_id, "response": text, "iterations": 0}
        if self.client:
            return self._chat_anthropic(session_id, message, history)
        return self._chat_compatible(session_id, message, history)

    def _chat_anthropic(self, session_id: str, message: str, history: list) -> dict:
        messages = history + [{"role":"user", "content":message}]
        for iteration in range(1, 13):
            response = self.client.messages.create(model=self.model, max_tokens=2048, system=SYSTEM_PROMPT, messages=messages, tools=TOOL_SCHEMAS)
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            text = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text")
            if not tool_uses:
                save_message(session_id, "user", message); save_message(session_id, "assistant", text)
                return {"session_id":session_id, "response":text, "iterations":iteration}
            messages.append({"role":"assistant","content":[block.model_dump() for block in response.content]})
            results = []
            for call in tool_uses:
                try: result = DISPATCH[call.name](**call.input)
                except Exception as exc: result = {"error": str(exc)}
                results.append({"type":"tool_result","tool_use_id":call.id,"content":json.dumps(result, ensure_ascii=False)})
            messages.append({"role":"user","content":results})
        return {"session_id":session_id,"response":"Je n'ai pas pu conclure après 12 itérations. Vous pouvez demander de continuer.","iterations":12}

    def _chat_compatible(self, session_id: str, message: str, history: list) -> dict:
        from openai import OpenAI
        client = OpenAI(api_key=self.chat_key, base_url=self.chat_base)
        messages = [{"role":"system","content":SYSTEM_PROMPT}] + history + [{"role":"user","content":message}]
        response = client.chat.completions.create(model=self.chat_model, max_tokens=2048, messages=messages)
        text = response.choices[0].message.content or ""
        save_message(session_id, "user", message); save_message(session_id, "assistant", text)
        return {"session_id":session_id, "response":text, "iterations":1}