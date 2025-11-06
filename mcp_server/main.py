
from fastapi import FastAPI, HTTPException
from firecrawl import Firecrawl
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# Initialize Firecrawl client with API key from environment
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
if not firecrawl_api_key:
    raise RuntimeError("FIRECRAWL_API_KEY not found in environment variables. Please create a .env file.")

firecrawl_client = Firecrawl(api_key=firecrawl_api_key)

@app.post("/scrape")
async def scrape_url(url: str):
    """
    Scrapes a single URL using Firecrawl and returns the markdown content.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required.")
    
    print(f"Received scrape request for URL: {url}")
    
    try:
        # Perform the scrape
        scraped_data = firecrawl_client.scrape(
            url=url,
            scrape_options={
                "onlyMainContent": True
            }
        )
        
        # The result is a ScrapeData object
        if scraped_data and scraped_data.markdown:
            print("Scrape successful, returning markdown.")
            return {"markdown": scraped_data.markdown}
        else:
            print("Scrape completed, but no markdown content was returned.")
            raise HTTPException(status_code=404, detail="Scrape did not return any markdown content.")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Firecrawl MCP Server is running."}
