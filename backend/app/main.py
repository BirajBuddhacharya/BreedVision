from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.middleware import add_middleware
from backend.app.routes import getImages, predict, test
from backend.app.services.predictor import load_model
from backend.app.config import MEDIA_DIR
import os

# Define lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()  # Load model once when FastAPI starts
    yield  # Continue with the application lifecycle
    
app = FastAPI(lifespan=lifespan)

# Apply middleware
add_middleware(app)

# Serve static files (enable media access)
os.makedirs(MEDIA_DIR, exist_ok=True)  # Ensure the media directory exists
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Include routers
app.include_router(test.router)
app.include_router(predict.router)
app.include_router(getImages.router)
