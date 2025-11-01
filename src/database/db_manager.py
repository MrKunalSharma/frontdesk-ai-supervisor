import os
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.local")


# Initialize Firebase only once (singleton)
firebase_app = None

def get_db():
    global firebase_app
    if not firebase_app:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        cred = credentials.Certificate(cred_path)
        firebase_app = firebase_admin.initialize_app(cred)
    return firestore.client()

def create_help_request(question, caller_id, timeout_minutes=30):
    db = get_db()
    doc_id = str(uuid.uuid4())
    now = datetime.utcnow()
    record = {
        "question": question,
        "caller_id": caller_id,
        "status": "pending",
        "created_at": now.isoformat() + "Z",
        "expires_at": (now + timedelta(minutes=timeout_minutes)).isoformat() + "Z",
        "response": None,
        "supervisor_id": None,
        "resolved_at": None
    }
    db.collection("help_requests").document(doc_id).set(record)
    return doc_id

def resolve_help_request(help_id, answer, supervisor_id, status="resolved"):
    db = get_db()
    doc_ref = db.collection("help_requests").document(help_id)
    doc_ref.update({
        "response": answer,
        "supervisor_id": supervisor_id,
        "status": status
    })

