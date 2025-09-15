from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.models import Base
from app.db.database import engine
from app.routers import pantry, recipe ,llm_recipes # add others as you create them

app = FastAPI(title="AI Digital Dietician API")

# ✅ CORS must be enabled, and allow OPTIONS + headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # <-- includes OPTIONS
    allow_headers=["*"],   # <-- include common/custom headers
)

# DB init
Base.metadata.create_all(bind=engine)

# Routes
@app.get("/health")
def health():
    return {"ok": True}

app.include_router(pantry.router)
app.include_router(recipe.router)
app.include_router(llm_recipes.router) 

from app.routers import pantry, recipe, plan
app.include_router(plan.router)
