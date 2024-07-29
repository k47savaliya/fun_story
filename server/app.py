import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.config import settings
from .api import api_router

app = FastAPI()

app.include_router(api_router, prefix="/v1")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)

@app.on_event("startup")
def make_directories():
    os.makedirs(settings.STATIC_FILE, exist_ok=True)


@app.get("/")
async def welcome():
    return {"status": 200, "message": "Server running"}
