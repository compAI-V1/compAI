from __future__ import annotations
import json, os
from anthropic import Anthropic
from .memory import get_history, save_message
from .system_prompt import SYSTEM_PROMPT
from tools import TOOL_SCHEMAS, DISPATCH

class Agent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    def chat(self, session_id: str, message: str) -> dict:
        history = get_history(session_id)
        if not self.client:
            text = "compAI est démarré, mais ANTHROPIC_API_KEY n'est pas configurée. Ajoutez-la dans .env pour activer l'agent Claude."
            save_message(session_id, "user", message); save_message(session_id, "assistant", text)
            return {"session_id": session_id, "response": text, "iterations": 0}
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
