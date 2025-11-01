import os
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')  # load once

KB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "knowledge_base.json"))

def load_kb():
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("[ERROR] Knowledge base file is corrupted, resetting KB!")
        # Optionally: backup the corrupted file before resetting
        return {}

def save_kb(kb):
    try:
        with open(KB_PATH, "w", encoding="utf-8") as f:
            json.dump(kb, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not save KB: {e}")

def add_answer(question, answer):
    kb = load_kb()
    kb[question.strip().lower()] = answer
    save_kb(kb)

def get_answer_from_kb(question, threshold=0.6):  # threshold for cosine sim
    kb = load_kb()
    norm_q = question.strip().lower()
    if norm_q in kb:
        return kb[norm_q]
    questions = list(kb.keys())
    if not questions:
        return None
    # semantic similarity
    embeddings = model.encode([norm_q] + questions, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(embeddings[0], embeddings[1:])[0]
    best_score = similarities.max().item()
    best_idx = similarities.argmax().item()
    if best_score > threshold:
        print(f"[INFO] EMBEDDING matched '{question}' to KB entry with score {best_score:.2f}")
        return kb[questions[best_idx]]
    return None
