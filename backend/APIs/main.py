from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from time import sleep

app = FastAPI()

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get('/test')
def test(): 
    sleep(5) # simulating work
    return {'message': 'test success'}