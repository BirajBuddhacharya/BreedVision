from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import ALLOWED_ORIGINS

def add_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
