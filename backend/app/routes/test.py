from fastapi import APIRouter
from time import sleep

router = APIRouter()

@router.get('/test/')
def test(): 
    sleep(5)  # Simulating work
    return {'message': 'test success'}
