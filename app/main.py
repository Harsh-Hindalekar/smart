from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import routes
from app.routes.ai_drawing import router as ai_router
from app.models import models

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GESTURE API",
    description="Backend for the project",
    version="1.0.0"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routes
app.include_router(routes.router, tags=["public"])

# ✅ INCLUDE AI DRAWING ROUTES (THIS WAS MISSING)
app.include_router(ai_router)

@app.get("/")
def read_root():
    return {"message": "Gesture API is running"}
