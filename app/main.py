"""Norsk Drill v3.0 – main entry point"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.db import init_db
from app.routers import practice, admin
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Norsk Drill", version="3.0", lifespan=lifespan)

# Static files (if folder exists)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(practice.router)
app.include_router(admin.router)
