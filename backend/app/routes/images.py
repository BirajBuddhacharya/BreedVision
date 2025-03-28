from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get('/getImage/')
async def get_image(): 
    file_path = r'C:\Users\admin\Desktop\BreedVision\backend\APIs\uploads\BIRAJ BUDDHACHARYA.png'
    return FileResponse(file_path, media_type="application/octet-stream")
