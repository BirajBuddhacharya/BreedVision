import sys; sys.path.append('.')
import torch
import logging 
from rich.logging import RichHandler
from backend.models.model import getModel
from PIL import Image
from torchvision.transforms import transforms
from backend.datasets.trainDataset import getDataset
import os 

# logging configurations
logging.basicConfig(
    level = logging.INFO, 
    handlers = [RichHandler(markup=True)], 
)
#global vairables 
...

def load_model(): 
    global model 
    global yolo 
    
    # Load YOLOv5 model
    os.chdir('backend/outputs') # loading yolo in outputs
    yolo = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    os.chdir('../..') # changing back to original dir 
    
    # loading model 
    model = getModel()
    model.load_state_dict(torch.load('backend/outputs/BreedClassifier.pth'))
    model.eval() # setting to eval mode
    
    
def predict(image: Image) -> str: 
    def clean(image: Image) -> Image:
        """
        Cleans and processes the input image using YOLOv5 to detect and crop a dog.

        Args:
            image (PIL.Image): The input image to be cleaned and processed.

        Returns:
            PIL.Image | None: A cropped image of the detected dog or None if no dog is detected or if there are multiple dogs.
        """
        if not yolo: 
            logging.info('yolo not loaded, loading now...')
            load_model()
    
        # Perform inference on the image
        results = yolo(image)
        df = results.pandas().xyxy[0]  # Extract prediction dataframe
        
        # If no dogs are detected or more than one, skip the image
        if df.empty or df.shape[0] > 1:
            logging.info("No dogs detected or more than one dog detected, skipping.")
            return None
        
        # Only consider the first row (single dog detection expected)
        row = df.iloc[0]
        
        # Skip if the detected object is not a dog
        if row['name'] != 'dog':
            logging.info('Skipping, no dog detected.')
            return None
        
        # Crop the image to the bounding box of the detected dog
        cropped_image = image.crop((row['xmin'], row['ymin'], row['xmax'], row['ymax']))
        
        return cropped_image
    
    if not model: 
        logging.info('Model not loaded, loading now...')
        load_model()
    
    # loading image
    image = image.convert("RGB")
    image = clean(image) # cleaning image (crop)
    
    if not image: 
        logging.error("Image doesn't contain dog or has more then 1 entity")
        return
    
    # transforming image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    transform_image =  transform(image).unsqueeze(0)  
    
    # predicting
    prediction = model(transform_image)
    prob, label_index = prediction.max(1)
    
    # loading labels from dataset
    dataset = getDataset()
    label_map = dataset.class_to_idx
    label_map = {v: k for k, v in label_map.items()} # inversing label map
    
    # getting label 
    label = label_map[label_index.item()]
    
    # returning dog name
    return label
    
if __name__ == '__main__': 
    image_path = r"C:\Users\admin\OneDrive\Desktop\gitProjects\BreedVision\backend\data\cleaned\pug\0_Healthy Pug Puppies for Sale in Palm River-Clair Mel, Florida ....jpg"
    image = Image.open(image_path)
    logging.info(predict(image))