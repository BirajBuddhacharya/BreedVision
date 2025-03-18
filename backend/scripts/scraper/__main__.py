import asyncio
import logging
from pathlib import Path
import aiohttp
from rich.logging import RichHandler
import sys; sys.path.append('.')
from backend.scripts.scraper.utils import *
from backend.config.breedList import dog_breeds  

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(markup=True)]
)
    
async def downloadBreed(breed: str, session = None): 
    # making folder to save downloaded images
    folder_name = breed.replace(' ', '_').lower()
    save_path = Path(f"backend/data/raw/{folder_name}")
    save_path.mkdir(exist_ok=True, parents= True)
    
     # skipping folder already has greater then 10 pictures
    if not len([item for item in save_path.iterdir()]) <= 10:
        logging.info(f"[blue]Skipping {breed}, folder already exists and has more then 10 pictures.[/blue]")
        return
    
    # making search virations
    search_query_variations = get_variations(breed)
    
    # searching for images
    async def search_download_image(session):
        '''
            searches for the image and downloads it
        '''
        search_tasks = [searchImage(session, variation) for variation in search_query_variations]
        search_results = await asyncio.gather(*search_tasks)
        search_results = [item for result in search_results for item in result] # modifying structure into single list of item
        
        # checking if search results exists (empty search if api key exhausted)
        if not search_results: 
            logging.info("Search is empty (API might be exhausted)")
            return
    
        # downloading images
        download_tasks = [download(session, data['link'], data['title'], save_path) for data in search_results]
        await asyncio.gather(*download_tasks)
        
    if session: 
        await search_download_image(session)
    else:
        async with aiohttp.ClientSession() as session: 
            await search_download_image(session)
        

async def main():
    """
        Main entry point to download images for all dog breeds.
    """
    
    async with aiohttp.ClientSession() as session:
        tasks = [downloadBreed(breed, session=session) for breed in dog_breeds]

        # for task in asyncio.as_completed(tasks):  # Process tasks as they complete
        #     result = await task
        #     if result is None:  # If any task fails, exit immediately
        #         logging.error("API KEY ALL EXHAUSTED EXITING...")
        #         sys.exit(1)  # Exit the program

        await asyncio.gather(*tasks)
        logging.info("All downloads completed successfully.")

if __name__ == '__main__':
    asyncio.run(main())