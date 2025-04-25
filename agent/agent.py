import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from tools.search import WebSearchTool
from tools.scraper import WebScraperTool
from tools.analyzer import ContentAnalyzerTool
import re

# Load environment variables (ensure .env file exists and is configured)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not found. Agent LLM features will fail.")

class WebResearchAgent:
    """Agent that researches user queries online."""

    def __init__(self, model_name="gemini-2.0-flash"):
        """
        Initializes the WebResearchAgent.

        Args:
            model_name: The name of the Gemini model to use for LLM tasks.
        """
        if not api_key:
            raise ValueError("Cannot initialize WebResearchAgent without GEMINI_API_KEY.")
        
        self.llm_model = genai.GenerativeModel(model_name)
        self.search_tool = WebSearchTool()
        self.scraper_tool = WebScraperTool()
        # Initialize analyzer tool here, it handles its own LLM setup
        self.analyzer_tool = ContentAnalyzerTool(model_name=model_name)
        self.max_search_results = 10  # Increased from 5 to 10
        self.max_sources_to_process = 7  # Increased from 3 to 7
        print(f"--- Web Research Agent initialized with model: {model_name} ---")

    def _analyze_query(self, query: str, context: str = None) -> dict:
        """Uses LLM to understand the query and suggest search terms, with optional context from previous interactions."""
        print(f"--- Analyzing query: {query} ---")
        
        # Include context if provided
        context_section = ""
        if context:
            context_section = f"""
            Additionally, consider this context from previous research:
            {context}
            
            Use this context to better understand the user's intent and refine your search strategy.
            """
            
        prompt = f"""Analyze the following research query and identify the core intent and key entities.
        Based on this, suggest a concise, effective search query (max 5 keywords) to use on a web search engine.

        Research Query: "{query}"{context_section}

        Output ONLY a JSON object with the following structure:
        {{
          "analysis": "Brief analysis of the user's intent.",
          "search_query": "Suggested search keywords."
        }}
        """
        try:
            response = self.llm_model.generate_content(prompt)
            # Basic cleaning and parsing
            cleaned_response = response.text.strip().strip('```json').strip('```').strip()
            result = json.loads(cleaned_response)
            print(f"--- Query Analysis Result: {result} ---")
            return result
        except Exception as e:
            print(f"--- Query analysis failed: {e}. Falling back to original query. ---")
            # Fallback strategy
            return {"analysis": "Analysis failed, using original query.", "search_query": query}

    def _synthesize(self, analyzed_data: list[dict], original_query: str, context: str = None) -> str:
        """Uses LLM to synthesize the findings into a coherent report with user-friendly formatting."""
        print(f"--- Synthesizing information from {len(analyzed_data)} sources for query: {original_query} ---")
        if not analyzed_data:
            return "No relevant information was found or successfully processed from the web search."

        # Prepare context for the LLM
        synthesis_context = f"Research Query: {original_query}\n\n" 
        
        # Add previous conversation context if available
        if context:
            synthesis_context += f"Previous Research Context:\n{context}\n\n"
            
        synthesis_context += "Sources Analyzed:\n"
        source_num = 1
        for item in analyzed_data:
            # Only include sources that were deemed relevant and successfully analyzed
            # Lowered the relevance threshold from 0.3 to 0.15
            if item.get('relevance_score', 0) > 0.15 and not item.get('error') and item.get('summary'):
                 synthesis_context += f"\n--- Source {source_num} (URL: {item.get('url', 'N/A')}) ---\n"
                 synthesis_context += f"Relevance Score: {item.get('relevance_score'):.2f}\n"
                 synthesis_context += f"Summary: {item.get('summary', 'N/A')}\n"
                 synthesis_context += "Key Points:\n"
                 for point in item.get('key_points', []):
                      synthesis_context += f"- {point}\n"
                 source_num +=1
            
        if source_num == 1: # No relevant sources made it into the context
            return "Found web sources, but none contained sufficiently relevant information after analysis."

        prompt = f"""Based *only* on the provided context from web sources below, synthesize a comprehensive and well-structured report answering the original research query.
        Address the query directly. Do not add any information not present in the sources.
        If sources contradict, point this out. Structure the report logically with clear paragraphs.
        
        IMPORTANT: Format the report for readability. DO NOT include source citations in the format "(Source X)".
        DO NOT use "**Key Points:**" or similar raw formatting markers. Instead, create a properly formatted report
        with clear sections and well-written paragraphs. If you need to mention sources, do so naturally in the text.
        
        {synthesis_context}

        Synthesized Report:
        """

        try:
            response = self.llm_model.generate_content(prompt)
            raw_text = response.text
            
            # Further clean up the response to make it user-friendly
            cleaned_text = raw_text
            
            # Remove source citation patterns
            cleaned_text = self._clean_source_citations(cleaned_text)
            
            # Format with HTML for better display
            formatted_html = self._format_as_html(cleaned_text)
            
            print("--- Synthesis successful ---")
            return formatted_html
        except Exception as e:
            print(f"--- Synthesis failed: {e} ---")
            return f"Error during synthesis: {e}. Partial data might be available in logs."

    def _clean_source_citations(self, text: str) -> str:
        """Clean up source citation patterns for better readability."""
        # Remove (Source X) patterns
        cleaned = re.sub(r'\(Source[s]? \d+(?:, \d+)*\)', '', text)
        # Remove (Sources X, Y, Z) patterns
        cleaned = re.sub(r'\(Sources \d+(?:, \d+)*(?:, \d+)*\)', '', cleaned)
        # Remove **Key Point:** and similar markers
        cleaned = re.sub(r'\*\*(.*?):\*\*', r'\1:', cleaned)
        # Remove excessive asterisks
        cleaned = cleaned.replace('**', '')
        # Fix double spaces
        cleaned = re.sub(r' +', ' ', cleaned)
        # Fix empty parentheses that might be left
        cleaned = re.sub(r'\(\s*\)', '', cleaned)
        return cleaned
        
    def _format_as_html(self, text: str) -> str:
        """Format the text as HTML for better display."""
        paragraphs = text.split('\n\n')
        html_parts = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Check if it's a heading (ends with colon or is all caps)
                if paragraph.strip().endswith(':') or paragraph.strip().isupper():
                    html_parts.append(f'<h3>{paragraph.strip()}</h3>')
                else:
                    html_parts.append(f'<p>{paragraph.strip()}</p>')
        
        return '\n'.join(html_parts)

    def research(self, query: str, 
                query_analysis_callback=None, 
                search_callback=None, 
                source_callback=None, 
                synthesis_callback=None) -> str:
        """Performs the end-to-end web research process."""
        print(f"=== Starting Research for Query: {query} ===")
        
        # 1. Analyze Query
        query_analysis = self._analyze_query(query)
        search_keywords = query_analysis.get('search_query', query)
        
        # Send query analysis result via callback
        if query_analysis_callback:
            query_analysis_callback(query_analysis)

        # 2. Search Web
        search_results = self.search_tool.search(search_keywords, num_results=self.max_search_results)
        
        # Send search results via callback
        if search_callback:
            search_callback(search_results)
        
        if not search_results:
            print("=== Research Complete (No Search Results) ===")
            return "Could not find any relevant web pages for the query."

        # 3. Scrape & Analyze Results (Iterative)
        analyzed_content_list = []
        processed_urls = set()
        urls_to_process = [r['url'] for r in search_results if r.get('url')]
        
        total_sources_to_process = min(len(urls_to_process), self.max_sources_to_process)
        source_number = 0

        for url in urls_to_process:
             if len(analyzed_content_list) >= self.max_sources_to_process:
                  print(f"--- Reached processing limit ({self.max_sources_to_process} sources) ---")
                  break # Stop processing if we hit the limit
            
             if url in processed_urls or not url:
                  continue # Skip duplicates or empty URLs

             source_number += 1
             processed_urls.add(url)
             
             # Get the title if available from search results
             title = next((r.get('title', 'Untitled') for r in search_results if r.get('url') == url), 'Untitled')
             
             # Notify start of source processing
             if source_callback:
                 source_callback(source_number, total_sources_to_process, url, title, "start")
             
             scrape_data = self.scraper_tool.scrape(url)

             if scrape_data['error']:
                 print(f"  Skipping analysis for {url} due to scraping error: {scrape_data['error']}")
                 # Optionally add error info to a list to report later
                 continue
            
             if scrape_data['raw_text']:
                 content_analysis = self.analyzer_tool.analyze(scrape_data['raw_text'], query)
                 # Store analysis result along with URL for synthesis context
                 analyzed_content_list.append({**content_analysis, 'url': url, 'title': title})
                 
                 # Add current relevance to the callback context
                 if source_callback:
                     if not content_analysis.get('error'):
                         source_callback(source_number, total_sources_to_process, url, title, "complete")
                 
                 if content_analysis.get('error'):
                      print(f"  Analysis for {url} resulted in error: {content_analysis['error']}")
                 else:
                      print(f"  Analysis for {url} complete. Relevance: {content_analysis.get('relevance_score', 0.0):.2f}")
             else:
                  print(f"  Skipping analysis for {url} as no text content was scraped.")

        # 4. Synthesize Findings
        if synthesis_callback:
            synthesis_callback()
        
        final_report = self._synthesize(analyzed_content_list, query)
        print(f"=== Research Complete for Query: {query} ===")
        return final_report

    def research_with_context(self, query: str, context: str,
                         query_analysis_callback=None, 
                         search_callback=None, 
                         source_callback=None, 
                         synthesis_callback=None) -> str:
        """
        Performs the end-to-end web research process with awareness of previous conversation context.
        
        Args:
            query: The research query from the user
            context: Previous conversation history/context
            callbacks: Various callback functions for progress tracking
            
        Returns:
            A comprehensive research report
        """
        print(f"=== Starting Context-Aware Research for Query: {query} ===")
        
        # 1. Analyze Query with context awareness
        query_analysis = self._analyze_query(query, context)
        search_keywords = query_analysis.get('search_query', query)
        
        # Send query analysis result via callback
        if query_analysis_callback:
            query_analysis_callback(query_analysis)

        # 2. Search Web
        search_results = self.search_tool.search(search_keywords, num_results=self.max_search_results)
        
        # Send search results via callback
        if search_callback:
            search_callback(search_results)
        
        if not search_results:
            print("=== Research Complete (No Search Results) ===")
            return "Could not find any relevant web pages for the query."

        # 3. Scrape & Analyze Results (Iterative)
        analyzed_content_list = []
        processed_urls = set()
        urls_to_process = [r['url'] for r in search_results if r.get('url')]
        
        total_sources_to_process = min(len(urls_to_process), self.max_sources_to_process)
        source_number = 0

        for url in urls_to_process:
             if len(analyzed_content_list) >= self.max_sources_to_process:
                  print(f"--- Reached processing limit ({self.max_sources_to_process} sources) ---")
                  break # Stop processing if we hit the limit
            
             if url in processed_urls or not url:
                  continue # Skip duplicates or empty URLs

             source_number += 1
             processed_urls.add(url)
             
             # Get the title if available from search results
             title = next((r.get('title', 'Untitled') for r in search_results if r.get('url') == url), 'Untitled')
             
             # Notify start of source processing
             if source_callback:
                 source_callback(source_number, total_sources_to_process, url, title, "start")
             
             scrape_data = self.scraper_tool.scrape(url)

             if scrape_data['error']:
                 print(f"  Skipping analysis for {url} due to scraping error: {scrape_data['error']}")
                 continue
            
             if scrape_data['raw_text']:
                 # Use context-aware analysis
                 content_analysis = self.analyzer_tool.analyze(scrape_data['raw_text'], query)
                 # Store analysis result along with URL for synthesis context
                 analyzed_content_list.append({**content_analysis, 'url': url, 'title': title})
                 
                 # Add current relevance to the callback context
                 if source_callback:
                     if not content_analysis.get('error'):
                         source_callback(source_number, total_sources_to_process, url, title, "complete")
                 
                 if content_analysis.get('error'):
                      print(f"  Analysis for {url} resulted in error: {content_analysis['error']}")
                 else:
                      print(f"  Analysis for {url} complete. Relevance: {content_analysis.get('relevance_score', 0.0):.2f}")
             else:
                  print(f"  Skipping analysis for {url} as no text content was scraped.")

        # 4. Synthesize Findings with context awareness
        if synthesis_callback:
            synthesis_callback()
        
        final_report = self._synthesize(analyzed_content_list, query, context)
        print(f"=== Context-Aware Research Complete for Query: {query} ===")
        return final_report

    def process_search_results(self, search_results: dict, query: str) -> list:
        """Process the search results, scrape and analyze content from the top results."""
        print(f"--- Processing search results for query: {query} ---")
        
        processed_results = []
        
        # Take top N results
        top_results = search_results.get("results", [])[:self.max_sources_to_process]
        
        if not top_results:
            print("--- No search results to process ---")
            return []
        
        for result in top_results:
            try:
                # Extract URL and title
                url = result.get("href", "")
                title = result.get("title", "No title")
                
                if not url:
                    continue
                    
                print(f"\n--- Processing result: {title} ---")
                print(f"--- URL: {url} ---")
                
                # Scrape content
                scraped_content = self.scraper_tool.scrape(url)
                
                if not scraped_content or len(scraped_content) < 100:  # Skip if too little content
                    print(f"--- Skipping {url}: insufficient content ---")
                    continue
                    
                # Analyze content
                analysis = self.analyzer_tool.analyze(scraped_content, query)
                
                # Check if analysis failed
                if analysis.get('error'):
                    print(f"--- Warning: Analysis had an error: {analysis.get('error')} ---")
                    # If there's an error but we still have a summary or key points, we can use them
                    if not analysis.get('summary') and not analysis.get('key_points'):
                        # Create a basic analysis based on the presence of keywords in the content
                        keywords = [kw for kw in self.analyzer_tool._extract_keywords(query) if len(kw) > 3]
                        if keywords and any(kw.lower() in scraped_content.lower() for kw in keywords):
                            # Create a minimal analysis with keyword-based extraction
                            print("--- Creating fallback analysis based on keywords ---")
                            analysis['relevance_score'] = 0.3  # Assign moderate-low relevance
                            analysis['summary'] = f"Content from {title} that may be relevant to {query}"
                            # Extract sentences containing keywords as key points
                            sentences = [s.strip() for s in scraped_content.split('.') if s.strip()]
                            relevant_sentences = []
                            for sentence in sentences[:100]:  # Look at first 100 sentences max
                                if any(kw.lower() in sentence.lower() for kw in keywords):
                                    relevant_sentences.append(sentence + '.')
                                    if len(relevant_sentences) >= 3:
                                        break
                            if relevant_sentences:
                                analysis['key_points'] = relevant_sentences
                
                # Filter out results with very low relevance
                if analysis.get('relevance_score', 0) < 0.1:
                    print(f"--- Skipping {url}: low relevance score {analysis.get('relevance_score')} ---")
                    continue
                    
                # Add to processed results
                processed_result = {
                    "title": title,
                    "url": url,
                    "summary": analysis.get("summary", ""),
                    "key_points": analysis.get("key_points", []),
                    "relevance_score": analysis.get("relevance_score", 0.0)
                }
                processed_results.append(processed_result)
                
            except Exception as e:
                print(f"--- Error processing result: {e} ---")
                continue
        
        # Sort by relevance score (high to low)
        processed_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        print(f"--- Processed {len(processed_results)} search results ---")
        return processed_results

# Example usage (for testing - requires API key in .env)
if __name__ == '__main__':
    if not api_key:
        print("Skipping WebResearchAgent test because GEMINI_API_KEY is not set.")
    else:
        agent = WebResearchAgent()
        # test_query = "What were the major announcements at Google I/O 2024 regarding AI?"
        test_query = "Compare and contrast the key features of React and Vue.js for frontend development."
        
        report = agent.research(test_query)
        
        print("\n\n======= FINAL REPORT =======\n")
        print(report)
        print("\n==========================\n") 