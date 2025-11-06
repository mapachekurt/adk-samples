
import os
import sys
from dotenv import load_dotenv
from firecrawl import Firecrawl

def main():
    """
    Main function to load environment variables, initialize Firecrawl,
    and start a crawl job.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not found in .env file.", file=sys.stderr)
        sys.exit(1)

    print("Starting crawl for https://google.github.io/adk-docs/...")

    try:
        # Initialize Firecrawl client
        client = Firecrawl(api_key=api_key)

        # Define crawl options
        crawler_options = {
            "limit": 100,
            "includes": ["/adk-docs/**"],
            "excludes": [],
        }
        page_options = {
            "onlyMainContent": True,
        }

        print(f"Calling crawl_url with url='https://google.github.io/adk-docs/', crawler_options={crawler_options}, page_options={page_options}")

        # Start the crawl job with corrected parameters and method
        crawl_result = client.crawl_url(
            url="https://google.github.io/adk-docs/",
            crawler_options=crawler_options,
            page_options=page_options
        )

        if crawl_result:
            output_filename = "adk_docs_scraped.md"
            print(f"Crawl finished. Scraped {len(crawl_result)} pages. Saving content to {output_filename}...")

            with open(output_filename, "w", encoding="utf-8") as f:
                # Combine all scraped markdown into one file
                for page in crawl_result:
                    f.write(f"# Source: {page['metadata']['sourceURL']}\n\n")
                    f.write(page['markdown'])
                    f.write("\n\n---\n\n")

            print(f"Full markdown content saved successfully to {output_filename}")

        else:
            print("Crawl job did not return any data.")

    except Exception as e:
        print(f"An error occurred during the crawl: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
