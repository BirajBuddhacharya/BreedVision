import cv2 
import pandas as pd 
import os 
import torch
import logging 
from rich.logging import RichHandler
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# global vairables
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True)]
)
rawPath = 'backend/data/raw/'

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def clean(dirPath, imgName):
    imgFullPath = os.path.join(dirPath, imgName)
    
    # exiting early if file doesn't exists 
    if not os.path.exists(imgFullPath): 
        logging.error("[red]Give Image doesn't exists[/red]")
        return 
    
    # configuring save path
    saveImgPath = dirPath.replace('raw', 'cleaned')
    if not os.path.exists(saveImgPath): 
        os.mkdir(saveImgPath) 
    
    # checking if image is already cleaned 
    cleanedImgNames = os.listdir(saveImgPath)
    if any(imgName in cleanedImgName for cleanedImgName in cleanedImgNames): 
        logging.warning(f'[yellow]Image already exists skipping {imgFullPath}[/yellow]')
        return
    
    # checking if image is openable 
    try: 
        Image.open(imgFullPath)
    except Exception as e: 
        logging.error(f"[red]Cant open image {imgFullPath}[/red]")
        return
    
    # cleaning image
    results = model(imgFullPath)
    df = results.pandas().xyxy[0]
    
    # returning if no dogs detected 
    if df.size == 0: 
        logging.info(f"No dogs detected skipping {imgFullPath}")
        return 
    
    # lopping through each image prediction: 
    for row in df.itertuples(): 
        # skipping if not a dog 
        if row.name != 'dog': 
            logging.info(f'{imgFullPath}: Skipping no dog entity')
            continue 
        
        # cropping image
        try: 
            image = cv2.imread(imgFullPath)
        except Exception as e: 
            logging.warning(f"[yellow]Cant open Image {imgFullPath}[/yellow]")
            return
        
        cropped_image = image[int(row.ymin) : int(row.ymax), int(row.xmin) : int(row.xmax)]

        # saving cropped image
        fullSavePath = os.path.join(saveImgPath, f'{row.Index}_{imgName}')
        cv2.imwrite(fullSavePath, cropped_image)
        logging.info(f'[green]cleaned {fullSavePath}[/green]')
        
def main(): 
    for dirPath, dirNames, fileNames in os.walk(rawPath): 
        with ThreadPoolExecutor(max_workers=40) as executor: 
            # repeating dirPaths to match fileNames
            dirPaths = [dirPath] * len(fileNames)
            executor.map(clean, dirPaths, fileNames)
        
if __name__ == '__main__': 
    main()