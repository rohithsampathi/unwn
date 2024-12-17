# app/services/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
from datetime import datetime
from typing import Dict, Optional

class FirebaseService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    async def store_conversation(self, user_id: str, conversation_id: str, data: Dict) -> bool:
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set({
                'conversations': {
                    conversation_id: {
                        'timestamp': datetime.now().isoformat(),
                        'data': data
                    }
                }
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error storing conversation: {e}")
            return False

    async def get_conversations(self, user_id: str) -> Optional[Dict]:
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else {"conversations": {}}
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return None