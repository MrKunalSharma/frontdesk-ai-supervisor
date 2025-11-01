import os
from ai_response import AIResponder
from database.db_manager import create_help_request

def on_message(message, sender):
    prompt = message['text']
    ai = AIResponder()
    response = ai.get_answer(prompt)
    if response is None:
        caller_id = sender if sender else "unknown"
        help_id = create_help_request(prompt, caller_id)
        print(f'Agent does not know the answer to: "{prompt}". Escalating to supervisor...')
        print(f'Help request logged. ID: {help_id}')
        print(f'NOTIFY SUPERVISOR: Need help answering: "{prompt}"')
        return "Let me check with my supervisor and get back to you."
    else:
        print(f'Agent answered directly: "{response}"')
        return response

if __name__ == "__main__":
    reply = on_message({"text": "Who is the owner?"}, "customer42")
    print("Agent reply:", reply)
    reply = on_message({"text": "Open hours?"}, "customer42")
    print("Agent reply:", reply)



