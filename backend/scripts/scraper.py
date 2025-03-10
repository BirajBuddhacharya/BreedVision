import requests
import os
from time import sleep 
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
# Google API details
API_KEY = os.getenv('API_KEY')
CX = os.getenv('CX')
QUERY = "german_shepard"  # Change the search keyword
NUM_IMAGES = 20      # Number of images to fetch
save_dir_path = '../data/raw/german_sheprad'

# Google Custom Search API URL
url = f"https://www.googleapis.com/customsearch/v1?q={QUERY}&cx={CX}&key={API_KEY}&searchType=image&num={NUM_IMAGES}"

# Fetch images
response = requests.get(url)
data = response.json()

print(data)
exit(1)

# Create folder to save images
os.makedirs(save_dir_path, exist_ok=True)

# Download images
for i, item in enumerate(data["items"]):
    img_url = item["link"]
    img_data = requests.get(img_url).content

    with open(f"{save_dir_path}/{QUERY}_{i+1}.jpg", "wb") as f:
        f.write(img_data)
        print(f"Downloaded {QUERY}_{i+1}.jpg")

print("Image download complete!")