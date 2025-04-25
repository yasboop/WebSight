import requests
from bs4 import BeautifulSoup
import time
import random

class WebScraperTool:
    """Tool for scraping web pages."""

    def scrape(self, url: str, timeout: int = 10) -> dict:
        """
        Scrapes the text content from a given URL.

        Args:
            url: The URL of the web page to scrape.
            timeout: The timeout in seconds for the request.

        Returns:
            A dictionary containing:
            - 'url': The original URL.
            - 'raw_text': The extracted text content, or None if scraping failed.
            - 'error': An error message if scraping failed, otherwise None.
        """
        print(f"--- Scraping URL: {url} ---")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Simulate network delay
            time.sleep(random.uniform(0.8, 2.0))
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text, trying to preserve some structure with spaces
            text = soup.get_text(separator=' ', strip=True)

            print(f"--- Successfully scraped {len(text)} characters from {url} ---")
            return {'url': url, 'raw_text': text, 'error': None}

        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            print(f"--- Scraping failed for {url}: {error_msg} ---")
            return {'url': url, 'raw_text': None, 'error': error_msg}
        except Exception as e:
            error_msg = f"An unexpected error occurred during scraping: {e}"
            print(f"--- Scraping failed for {url}: {error_msg} ---")
            return {'url': url, 'raw_text': None, 'error': error_msg}

# Example usage (for testing)
if __name__ == '__main__':
    scraper_tool = WebScraperTool()
    test_url = "https://example.com" # A simple, reliable page
    # test_url = "https://ai.google.dev/docs" # A more complex page
    result = scraper_tool.scrape(test_url)

    if result['error']:
        print(f"Error scraping {test_url}: {result['error']}")
    elif result['raw_text']:
        print(f"\nScraped Content (first 500 chars):\n{result['raw_text'][:500]}...")
    else:
        print(f"No text content found for {test_url}, but no error reported.") 