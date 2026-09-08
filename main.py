from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.resume import router as resume_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✅ Database initialized successfully")

    yield

    print("🔴 Application shutting down")


app = FastAPI(
    title="ResumeAI Core Backend Engine",
    description="Industry standard modular architecture",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router,
    prefix="/api"
)

app.include_router(
    resume_router,
    prefix="/api"
)


@app.get("/")
async def root():
    return {
        "status": "Master Gateway Server is Online!"
    }