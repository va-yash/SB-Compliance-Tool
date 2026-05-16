from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base
import models  # noqa: F401 — ensure models are registered before create_all
from routers import aircraft, sb

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SB Compliance Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(aircraft.router)
app.include_router(sb.router)


@app.get("/")
def root():
    return {"status": "ok", "app": "SB Compliance Tool", "version": "1.0.0"}
