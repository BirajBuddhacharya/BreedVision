import os
import re
import aiohttp  # Use aiohttp instead of requests
from dotenv import load_dotenv
import logging 
from rich.logging import RichHandler
import asyncio

import sys; sys.path.append('.')
from backend.config.breedList import dog_breeds

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(markup=True)]
)
# Adjust the logging level for the requests module
logging.getLogger('aiohttp').setLevel(logging.WARNING)  # This will suppress debug messages

def sanitize_filename(title):
    """Removes invalid characters from filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", title)

async def extract(query, num, save_path):
    async def fetcher(session, link, title): 
        """Fetches an image and saves it to the specified path."""
        try:
            img_url = link
            sanitized_title = sanitize_filename(title)
            file_path = os.path.join(save_path, f"{sanitized_title}.jpg")
            
            # leaving early if duplicate exists
            if os.path.exists(file_path): 
                logging.warning("File exists no changes made")
                return
                        
            async with session.get(img_url, timeout=10) as response:  # Using aiohttp's asynchronous get
                response.raise_for_status()  # Raise an error for failed requests

                with open(file_path, "wb") as f:
                    f.write(await response.read())  # Read content asynchronously

            logging.info(f"[green]✔ {sanitized_title}.jpg[/green]")  
        except aiohttp.ClientError as e:
            logging.error(f"[red]❌ Failed: {title} ({e})[/red]")  

    # Load API keys
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    CX = os.getenv('CX')

    # Google Custom Search API URL
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX}&key={API_KEY}&searchType=image&num={num}"

    try:
        async with aiohttp.ClientSession() as session:  # Create a session for all requests
            async with session.get(url, timeout=20) as response:
                response.raise_for_status()
                data = await response.json()  # Parse response asynchronously
                
    except aiohttp.ClientError as e:
        logging.error(f"API request failed: {e}")
        exit(0)

    # Catch API errors
    if "error" in data:
        logging.error(f"Error found: {data['error']['code']} - {data['error']['message']}")
        exit(0)

    # Extract image links and titles
    image_links = [item['link'] for item in data.get('items', [])]
    image_titles = [item['title'] for item in data.get('items', [])]

    if not image_links:
        logging.info("No images found.")
        return

    # Create folder to save images
    os.makedirs(save_path, exist_ok=True)

    # Download images with asyncio
    tasks = [fetcher(session, image_link, image_title) for image_link, image_title in zip(image_links, image_titles)]
    
    await asyncio.gather(*tasks)

    logging.info(f"Image download complete for {query}!")

def getVeriations(breed): 
    variations = [
        breed, 
        'puppies ' + breed, 
        'old ' + breed, 
        'cute ' + breed, 
        'funny ' + breed, 
        'happy ' + breed, 
        'sad ' + breed, 
        'angry ' + breed, 
        'sleepy ' + breed, 
        'playful ' + breed
    ]
    return variations

async def getDog(breed): 
    variations = getVeriations(breed)
    
    folder_name = breed.replace(' ', '_').lower()
    full_path =  f'backend/data/raw/{folder_name}/'
    
    # skipping already existing breeds
    if os.path.exists(full_path): 
        logging.info("[blue]Path already exists[/blue]")
        return
    
    tasks = [extract(variation, 10, f'backend/data/raw/{full_path}/') for variation in variations]

    await asyncio.gather(*tasks)
    
async def main():
    breeds = dog_breeds
    
    for breed in breeds: 
        await getDog(breed)
    
if __name__ == '__main__': 
    asyncio.run(getDog("Scottish Terrier"))
