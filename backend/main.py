import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.prediction import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Manufacturing Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Manufacturing Intelligence API v1.0"}
