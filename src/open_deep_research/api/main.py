from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from open_deep_research.api.routes import router

app = FastAPI(title="Open Deep Research API")

# Enable CORS (for frontend compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. Lock down in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "LangGraph API is running"}
