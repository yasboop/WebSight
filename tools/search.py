from duckduckgo_search import DDGS
import time
import random

class WebSearchTool:
    """Tool for performing web searches using DuckDuckGo."""

    def search(self, query: str, num_results: int = 5) -> list[dict]:
        """
        Performs a web search for the given query.

        Args:
            query: The search query string.
            num_results: The maximum number of results to return.

        Returns:
            A list of dictionaries, where each dictionary represents a search result
            and contains 'title', 'href' (URL), and 'body' (snippet).
            Returns an empty list if the search fails.
        """
        print(f"--- Performing web search for: {query} ---")
        
        # First attempt with original query
        results = self._perform_search(query, num_results)
        
        # If no results are found, try simplifying the query
        if not results:
            simplified_query = self._simplify_query(query)
            if simplified_query != query:
                print(f"--- No results found with original query. Trying simplified query: {simplified_query} ---")
                results = self._perform_search(simplified_query, num_results)
        
        return results
    
    def _perform_search(self, query: str, num_results: int) -> list[dict]:
        """Helper method to perform the actual search."""
        try:
            # Use DDGS context manager for potentially cleaner resource handling
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
            
            # Simulate network delay slightly
            time.sleep(random.uniform(0.5, 1.5))

            if not results:
                print("--- No results found. ---")
                return []

            # Format results to match expected output structure
            formatted_results = [
                {'title': r.get('title', ''), 'url': r.get('href', ''), 'snippet': r.get('body', '')}
                for r in results
            ]
            print(f"--- Found {len(formatted_results)} results. ---")
            return formatted_results
        except Exception as e:
            print(f"--- Web search failed: {e} ---")
            return []
    
    def _simplify_query(self, query: str) -> str:
        """
        Simplifies a complex query by extracting key terms.
        This can help when the original query doesn't return results.
        """
        # Split by spaces and keep only words that are 4+ characters
        words = query.split()
        
        # Remove common stop words
        stop_words = {'about', 'tell', 'what', 'where', 'when', 'which', 'who', 'whom', 'whose', 'why', 'how'}
        
        # Keep important words (not in stop_words and at least 4 chars long)
        important_words = [word for word in words if len(word) >= 4 and word.lower() not in stop_words]
        
        # If we have at least 2 important words, use those
        if len(important_words) >= 2:
            return ' '.join(important_words)
        # Otherwise return the original query
        return query

# Example usage (for testing)
if __name__ == '__main__':
    search_tool = WebSearchTool()
    test_query = "Benefits of Python for web development"
    results = search_tool.search(test_query, num_results=3)
    if results:
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Title: {result['title']}")
            print(f"  URL: {result['url']}")
            print(f"  Snippet: {result['snippet']}\n")
    else:
        print("Search returned no results.") 