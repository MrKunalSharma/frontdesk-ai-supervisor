class OpenAIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_response(self, prompt):
        # Mock response instead of real OpenAI call
        return "Sorry, I do not know the answer to your question. Let me check with my supervisor and get back to you."
