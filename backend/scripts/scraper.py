import os
import re
import asyncio
import logging
from pathlib import Path
import aiohttp
from dotenv import load_dotenv
from rich.logging import RichHandler

import sys
sys.path.append('.')
from backend.config.breedList import dog_breeds  

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(markup=True)]
)

# Suppress unnecessary debug logs from aiohttp
logging.getLogger('aiohttp').setLevel(logging.WARNING)

# Load API keys
load_dotenv()
API_KEY = os.getenv('API_KEY')
CX = os.getenv('CX')

# Ensure API keys are available
if not API_KEY or not CX:
    logging.critical("[red]API_KEY or CX is missing! Check your .env file.[/red]")
    exit(1)

def sanitize_filename(title: str) -> str:
    """
        Removes invalid characters from filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", title)

async def fetch_image(session: aiohttp.ClientSession, url: str, title: str, save_path: Path):
    """
        Fetch and save an image asynchronously.
    """
    try:
        sanitized_title = sanitize_filename(title)
        file_path = save_path / f"{sanitized_title}.jpg"

        if file_path.exists():
            logging.warning(f"[yellow]Skipping: {sanitized_title}.jpg (Already Exists)[/yellow]")
            return

        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            file_path.write_bytes(await response.read())

        logging.info(f"[green]✔ Downloaded: {sanitized_title}.jpg[/green]")

    except aiohttp.ClientError as e:
        logging.error(f"[red]❌ Failed to download {title}: {e}[/red]")

async def extract_images(session: aiohttp.ClientSession, query: str, num: int, save_path: Path):
    """
        Fetch image URLs and download them asynchronously.
    """
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX}&key={API_KEY}&searchType=image&num={num}"

    try:
        async with session.get(url, timeout=20) as response:
            response.raise_for_status()
            data = await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"[red]API request failed: {e}[/red]")
        exit(0)

    # Handle API errors
    if "error" in data:
        logging.error(f"[red]API Error {data['error']['code']}: {data['error']['message']}[/red]")
        exit(0)

    # Extract image links and titles
    images = data.get('items', [])
    if not images:
        logging.info(f"[blue]No images found for {query}[/blue]")
        return

    save_path.mkdir(parents=True, exist_ok=True)
    tasks = [fetch_image(session, item['link'], item['title'], save_path) for item in images]

    await asyncio.gather(*tasks)
    logging.info(f"[green]✔ Image download complete for {query}![/green]")

def get_variations(breed: str):
    """
        Generate variations of a dog breed search query.
    """
    
    return [
        breed, f"puppies {breed}", f"old {breed}", f"cute {breed}", f"funny {breed}",
        f"happy {breed}", f"sad {breed}", f"angry {breed}", f"sleepy {breed}", f"playful {breed}"
    ]

async def fetch_dog_images(session: aiohttp.ClientSession, breed: str):
    """
        Download images for a given dog breed with variations.
    """
    
    variations = get_variations(breed)
    folder_name = breed.replace(' ', '_').lower()
    save_path = Path(f"backend/data/raw/{folder_name}")

    if save_path.exists():
        logging.info(f"[blue]Skipping {breed}, folder already exists.[/blue]")
        return

    tasks = [extract_images(session, variation, 10, save_path) for variation in variations]
    await asyncio.gather(*tasks)

async def main():
    """
        Main entry point to download images for all dog breeds.
    """
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_dog_images(session, breed) for breed in dog_breeds]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(fetch_dog_images(aiohttp.ClientSession(), "Scottish Terrier"))
