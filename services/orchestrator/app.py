from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .orchestrator import FlowMindOrchestrator
from ..pedagogy.feedback_service import FeedbackService, FeedbackRequest
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FlowMind Orchestrator")
orchestrator = FlowMindOrchestrator()
feedback_service = FeedbackService()

class IngestRequest(BaseModel):
    pdf_path: str

class QueryRequest(BaseModel):
    query: str

@app.post("/ingest")
async def ingest(request: IngestRequest):
    try:
        result = await orchestrator.ingest_pdf(request.pdf_path)
        if not result.success:
            raise HTTPException(status_code=500, detail=result.payload.get("error"))
        return result.payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /ingest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(request: QueryRequest):
    try:
        result = await orchestrator.ask_tutor(request.query)
        if not result.success:
            raise HTTPException(status_code=500, detail=result.payload.get("error"))
        return result.payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /ask: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        logger.info(f"Received feedback for query: {request.query[:30]}...")
        return feedback_service.submit_feedback(request)
    except Exception as e:
        logger.error(f"Error in /feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
