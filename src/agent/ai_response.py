import os
from knowledge_base import get_answer_from_kb

class AIResponder:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def get_answer(self, prompt):
        try:
            kb_answer = get_answer_from_kb(prompt)
        except Exception as e:
            print("[ERROR] KB access failed:", e)
            kb_answer = None

        if kb_answer:
            return kb_answer
        # fallback agent logic (as before)
        knows = "address" in prompt.lower() or "time" in prompt.lower()
        if knows:
            return "Our salon is open from 10am to 8pm at 123 Main Street."
        return None
