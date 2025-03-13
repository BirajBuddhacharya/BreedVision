from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from time import sleep
import matplotlib.pyplot as plt 
from PIL import Image
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get('/test/')
def test(): 
    sleep(5) # simulating work
    return {'message': 'test success'}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)): 
    image = Image.open(file.file)
    
    return {"breed": "Test Breed", "description": "This is a dummy description for the uploaded image."}

@app.get('/getImage/')
async def getImage(): 
    file_path = r'C:\Users\admin\Desktop\BreedVision\backend\APIs\uploads\BIRAJ BUDDHACHARYA.png'
    return FileResponse(file_path, media_type="application/octet-stream")