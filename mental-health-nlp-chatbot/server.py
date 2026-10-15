"""
FastAPI Web Server for Mental Health NLP Chatbot & CDC Indicators Dashboard.
Serves static assets and provides RESTful API endpoints for chat inference,
dataset analytics, demographic comparisons, and clinical screening.
"""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from chat import get_response, _engine, bot_name
from dataset_analytics import analytics_engine

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Aura Mental Health AI & CDC Analytics",
    description="Contextual Mental Health Chatbot with CDC Anxiety and Depression Indicators EDA Dashboard",
    version="2.0.0",
)


# Request & Response Schemas
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    bot_name: str = bot_name
    tag: Optional[str] = None
    confidence: float = 0.0


class ScreenRequest(BaseModel):
    anxiety_q1: int  # 0-3 (Nervous, anxious, on edge)
    anxiety_q2: int  # 0-3 (Not being able to stop or control worrying)
    depression_q3: int  # 0-3 (Little interest or pleasure in doing things)
    depression_q4: int  # 0-3 (Feeling down, depressed, or hopeless)
    age_group: Optional[str] = None


# API Routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """Process user message through Aura NLP engine and return response."""
    msg = payload.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    tag, confidence = _engine.predict_intent(msg)
    reply = get_response(msg)

    return ChatResponse(
        reply=reply,
        bot_name=bot_name,
        tag=tag,
        confidence=round(confidence, 3),
    )


@app.get("/api/dataset/summary")
async def dataset_summary():
    """Return top-level KPIs, national averages, and survey dimensions."""
    return analytics_engine.get_summary()


@app.get("/api/dataset/trends")
async def dataset_trends():
    """Return longitudinal national trends across survey periods."""
    return analytics_engine.get_trends()


@app.get("/api/dataset/demographics")
async def dataset_demographics(group: str = "By Age"):
    """Return latest prevalence breakdown by demographic group."""
    valid_groups = [
        "By Age",
        "By Sex",
        "By Education",
        "By Race/Hispanic ethnicity",
        "By Disability status",
        "By Sexual orientation",
    ]
    if group not in valid_groups:
        group = "By Age"
    return {
        "group": group,
        "data": analytics_engine.get_demographics(group),
    }


@app.get("/api/dataset/states")
async def dataset_states():
    """Return state-by-state latest rates."""
    return analytics_engine.get_state_metrics()


@app.post("/api/screen")
async def screen_endpoint(payload: ScreenRequest):
    """Calculate PHQ-4 screener score and benchmark against population data."""
    anxiety_score = max(0, min(6, payload.anxiety_q1 + payload.anxiety_q2))
    depression_score = max(0, min(6, payload.depression_q3 + payload.depression_q4))

    result = analytics_engine.benchmark_screener(
        anxiety_score=anxiety_score,
        depression_score=depression_score,
        age_group=payload.age_group,
    )
    return result


# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """Serve single page web application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Aura Health AI Server is running. Frontend static index.html not yet initialized."}


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Launch uvicorn server."""
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("=" * 60)
    print(f"[*] Aura Mental Health Web App starting at: http://{host}:{port}")
    print("=" * 60)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
