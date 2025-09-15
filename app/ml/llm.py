# apps/api/app/ml/llm.py
import json, re, traceback
import httpx
from typing import Dict, Any
from fastapi import HTTPException
from app.core.config import get_settings

settings = get_settings()

def _extract_json_obj(s: str) -> Dict[str, Any]:
    """
    Try strict parse; if it fails, extract the largest {...} block and parse that.
    Handles cases where models wrap JSON with text.
    """
    s = s.strip()
    # 1) strict
    try:
        return json.loads(s)
    except Exception:
        pass
    # 2) find first '{' and last '}' and try substring
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            # 3) last resort: grab the first JSON object via regex (non-greedy, balanced-ish)
            # This won’t be perfect for deeply nested, but good enough for LLM outputs.
            m = re.search(r"\{.*\}", s, re.DOTALL)
            if m:
                return json.loads(m.group(0))
    raise HTTPException(status_code=500, detail=f"Ollama JSON parse failed. content={s[:300]}...")

class LLMProvider:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        return self._ollama_json(prompt)

    def _ollama_json(self, prompt: str) -> Dict[str, Any]:
        """
        Calls Ollama chat API with format=json and stream=False,
        then tolerantly extracts a JSON object from the response.
        """
        url = f"{self.ollama_url}/api/chat"
        body = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": "Return STRICT JSON ONLY. No prose. Keys: title, ingredients(array of strings), instructions(array of strings), macros(object with calories, protein, carbs, fat)."},
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "options": {"temperature": 0.3},
            "stream": False  # 🔒 ensure a single, non-streamed response
        }
        try:
            with httpx.Client(timeout=120) as client:
                r = client.post(url, json=body)
                if r.status_code >= 400:
                    raise HTTPException(status_code=r.status_code, detail=r.text)
                data = r.json()
                # Ollama chat returns: {"message":{"role":"assistant","content":"..."},"done":true,...}
                raw = (data.get("message") or {}).get("content", "")
                if not raw:
                    raise HTTPException(status_code=500, detail=f"Ollama returned empty content: {data}")
                return _extract_json_obj(raw)
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Ollama call failed: {e}")
