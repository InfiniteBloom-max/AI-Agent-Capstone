from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
from datetime import datetime

class FeedbackRequest(BaseModel):
    query: str
    response: str
    rating: int  # 1-5
    comments: Optional[str] = None
    improved_response: Optional[str] = None

class FeedbackService:
    def __init__(self, storage_path: str = "data/feedback.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    def submit_feedback(self, feedback: FeedbackRequest):
        """Store feedback and potentially trigger improvement logic"""
        entry = feedback.dict()
        entry['timestamp'] = datetime.now().isoformat()
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        data.append(entry)
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        return {"status": "success", "message": "Feedback received"}

    def get_feedback_stats(self):
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        return {
            "total_feedback": len(data),
            "average_rating": sum(d['rating'] for d in data) / len(data) if data else 0
        }
