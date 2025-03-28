from fastapi import APIRouter, UploadFile, File
from PIL import Image
from backend.app.services.predictor import predict

router = APIRouter()

@router.post("/predict/")
async def predict_breed(file: UploadFile = File(...)): 
    image = Image.open(file.file)
    dog_breed = predict(image) 
    dog_breed = dog_breed if dog_breed else "Unknown"
    
    return {"breed": dog_breed, "description": "This is a dummy description for the uploaded image."}
