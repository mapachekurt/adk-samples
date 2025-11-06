
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
        firecrawl = Firecrawl(api_key=api_key)

        # Start the crawl job
        crawl_result = firecrawl.crawl(
            url="https://google.github.io/adk-docs/",
            params={
                "crawlerOptions": {
                    "limit": 100,
                    "includes": ["/adk-docs/**"], # Crawl only pages under the /adk-docs/ path
                    "excludes": [],
                },
                "pageOptions": {
                    "onlyMainContent": True, # Extract clean content
                }
            }
        )
        
        # The crawl() method in the Python SDK is synchronous and waits for the result
        # It returns a list of scraped data objects.
        if crawl_result:
            print(f"Crawl finished successfully! Scraped {len(crawl_result)} pages.")
            # You can process the results here. For now, we'll just print a summary.
            for i, page in enumerate(crawl_result):
                print(f"  - Page {i+1}: {page['metadata']['sourceURL']} ({len(page['markdown'])} chars)")
            
            # Example of saving the first page's markdown to a file
            if len(crawl_result) > 0:
                output_filename = "adk_docs_scraped.md"
                with open(output_filename, "w", encoding="utf-8") as f:
                    # Combine all scraped markdown into one file
                    for page in crawl_result:
                        f.write(f"# Source: {page['metadata']['sourceURL']}\n\n")
                        f.write(page['markdown'])
                        f.write("\n\n---\n\n")
                print(f"\nFull markdown content saved to {output_filename}")

        else:
            print("Crawl job did not return any data.")

    except Exception as e:
        print(f"An error occurred during the crawl: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
