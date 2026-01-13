from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Smart City Orchestrator")
app.include_router(router)