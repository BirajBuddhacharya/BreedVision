import re
import aiohttp
import logging
from dotenv import load_dotenv
import os
from pathlib import Path
import asyncio

# Load API keys
load_dotenv()
API_KEY = os.getenv('API_KEY').split(',')
CX = os.getenv('CX').split(',')

# Ensure API keys are available
if not API_KEY or not CX:
    logging.critical("[red]API_KEY or CX is missing! Check your .env file.[/red]")
    exit(1)

def sanitize_filename(title: str) -> str:
    """
        Removes invalid characters from filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", title)

def get_variations(breed: str):
    """
        Generate variations of a dog breed search query.
    """
    
    return [
        breed, f"puppies {breed}", f"old {breed}", f"cute {breed}", f"funny {breed}",
        f"happy {breed}", f"sad {breed}", f"angry {breed}", f"sleepy {breed}", f"playful {breed}"
    ]

async def searchImage(session, query): 
    num = 10
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX[-1]}&key={API_KEY[-1]}&searchType=image&num={num}"

    try:
        async with session.get(url, timeout=20) as response:
            response.raise_for_status()
            data = await response.json()
    except aiohttp.ClientError as e:
        if e.status == 429:
            # checking no API_KEY
            if not API_KEY or not CX: 
                logging.error(f"[red]All API key exhausted exiting for now: {e}[/red]")
                return []
            
            # switching exhausted apikey
            API_KEY.pop()
            CX.pop()
            

            logging.info("API Key exhausted switching API Key")
            return await searchImage(session, query)
            
        logging.error(f"[red]API request failed: {e}[/red]")
        return []
        
    return [{'link': i['link'], 'title': i['title']} for i in data.get('items', [])]

async def download(session: aiohttp.ClientSession, url: str, title: str, save_path: Path):
    """
        Fetch and save an image asynchronously.
    """
    try:
        sanitized_title = sanitize_filename(title)
        file_path = save_path / f"{sanitized_title}.jpg"

        if file_path.exists():
            logging.warning(f"[yellow]Skipping: {sanitized_title}.jpg (Already Exists)[/yellow]")
            return

        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                file_path.write_bytes(await response.read())
                
            logging.info(f"[green]✔ Downloaded: {sanitized_title}.jpg[/green]")
            
        except asyncio.TimeoutError:
            logging.error(f"[red]❌ Timeout error while downloading {title}[/red]")


    except aiohttp.ClientError as e:
        logging.error(f"[red]❌ Failed to download {title}: {e}[/red]")