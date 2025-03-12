import os
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from dotenv import load_dotenv

def sanitize_filename(title):
    """Removes invalid characters from filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", title)

def extract(query, num, save_path):
    downloaded = []
    errors = []

    def fetcher(link, title): 
        """Fetches an image and saves it to the specified path."""
        try:
            img_url = link
            response = requests.get(img_url, timeout=10)  # Set timeout to prevent hanging
            response.raise_for_status()  # Raise an error for failed requests

            sanitized_title = sanitize_filename(title)
            file_path = os.path.join(save_path, f"{sanitized_title}.jpg")

            with open(file_path, "wb") as f:
                f.write(response.content)

            downloaded.append(f"[green]✔ {sanitized_title}.jpg[/green]")  
        except requests.RequestException as e:
            errors.append(f"[red]❌ Failed: {title} ({e})[/red]")  

    # Load API keys
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    CX = os.getenv('CX')

    # Google Custom Search API URL
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CX}&key={API_KEY}&searchType=image&num={num}"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return

    # Catch API errors
    if "error" in data:
        print(f"Error found: {data['error']['code']} - {data['error']['message']}")
        return

    # Extract image links and titles
    image_links = [item['link'] for item in data.get('items', [])]
    image_titles = [item['title'] for item in data.get('items', [])]

    if not image_links:
        print("No images found.")
        return

    # Create folder to save images
    os.makedirs(save_path, exist_ok=True)

    # Dynamic UI update
    with Live(refresh_per_second=4) as live:
        def update_ui():
            panel_downloaded = Panel("\n".join(downloaded) or "[yellow]No downloads yet[/yellow]", title="Downloaded Summary", border_style="green")
            panel_errors = Panel("\n".join(errors) or "[yellow]No errors yet[/yellow]", title="Errors", border_style="red")
            live.update(Columns([panel_downloaded, panel_errors]))

        # Download images with threading
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetcher, link, title) for link, title in zip(image_links, image_titles)]
            
            for future in futures:
                future.result()  # Ensure each thread completes
                update_ui()  # Refresh UI after each download attempt

    print("Image download complete!")

def main(): 
    dog_breeds = ["Rottweiler"]

    for breed in dog_breeds: 
        save_path = breed.replace(' ', '_').lower()
        extract(breed, 10, f'backend/data/raw/{save_path}/')
        break # for debugging

if __name__ == '__main__': 
    main()