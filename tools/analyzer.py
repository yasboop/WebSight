import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables. Analyzer tool will not work.")

class ContentAnalyzerTool:
    """Tool for analyzing scraped web content using an LLM."""

    def __init__(self, model_name="gemini-2.0-flash"):
        """
        Initializes the ContentAnalyzerTool.

        Args:
            model_name: The name of the Generative AI model to use.
        """
        if not api_key:
             raise ValueError("Cannot initialize ContentAnalyzerTool without GEMINI_API_KEY.")
        try:
             # Set safety settings to be more permissive for content analysis
             safety_settings = [
                 {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                 {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                 {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                 {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
             ]
             
             self.model = genai.GenerativeModel(
                 model_name,
                 safety_settings=safety_settings,
                 generation_config={"temperature": 0.1, "response_mime_type": "application/json"}  # Force JSON response
             )
             print(f"--- Content Analyzer initialized with model: {model_name} ---")
        except Exception as e:
             print(f"--- Failed to initialize Generative Model: {e} ---")
             raise

    def analyze(self, content: str, query_context: str) -> dict:
        """
        Analyzes the provided text content for relevance to the query context.

        Args:
            content: The text content scraped from a web page.
            query_context: The original user query or relevant sub-question.

        Returns:
            A dictionary containing:
            - 'summary': A concise summary of the relevant information.
            - 'key_points': A list of key takeaways related to the query.
            - 'relevance_score': A float between 0.0 and 1.0 indicating relevance.
            - 'error': An error message if analysis failed, otherwise None.
        """
        print(f"--- Analyzing content (length: {len(content)}) for query: {query_context} ---")

        # Truncate content if too long to avoid excessive API costs/time
        max_len = 50000 # Adjust as needed
        if len(content) > max_len:
            print(f"--- Content truncated from {len(content)} to {max_len} characters for analysis ---")
            content = content[:max_len]

        # Extract keywords from the query to help with relevance determination
        keywords = self._extract_keywords(query_context)
        keywords_str = ", ".join(keywords) if keywords else query_context
        
        # Use a clearer, more explicit prompt optimized for JSON output
        prompt = f"""<task>
CONTENT ANALYSIS TASK: Analyze web content to determine its relevance to a search query.

WEB CONTENT:
{content}

SEARCH QUERY:
"{query_context}"

KEY TERMS TO FOCUS ON:
{keywords_str}

ANALYSIS GUIDELINES:
- Determine if the content contains information relevant to the query
- Be generous with relevance - if there's ANY helpful information, consider it relevant
- Write a concise summary (up to 200 words) of the relevant information
- Extract 3-5 key points related to the query
- Assign a relevance score between 0.0 and 1.0:
  * 0.1-0.3: Minimal relevance (mentions key terms but little useful information)
  * 0.4-0.6: Moderate relevance (has helpful information but not comprehensive)
  * 0.7-1.0: High relevance (directly addresses the query with substantial information)

OUTPUT FORMAT:
You must output ONLY a valid JSON object with these exact keys:
{{
  "summary": "Your concise summary here",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "relevance_score": 0.7
}}
</task>"""

        try:
            # Generate content using the Gemini model with structured format
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # Enhanced logic to parse potentially malformed responses
            try:
                if not hasattr(response, 'text') or not response.text:
                    print("--- Analysis failed: Empty response from model ---")
                    return self._create_fallback_response("Empty response from model")
                
                raw_text = response.text
                print(f"--- Raw response length: {len(raw_text)} characters ---")
                
                # First try direct JSON parsing
                try:
                    # Clean potential markdown formatting from the response
                    json_str = raw_text.strip()
                    if json_str.startswith('```json'):
                        json_str = json_str[7:]
                    if json_str.endswith('```'):
                        json_str = json_str[:-3]
                    json_str = json_str.strip()
                    
                    analysis_result = json.loads(json_str)
                    print("--- Analysis successful with direct JSON parsing ---")
                    
                    # Validate required keys exist
                    self._validate_and_fix_keys(analysis_result)
                    analysis_result['error'] = None
                    return analysis_result
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON using regex
                    json_pattern = r'({[\s\S]*})'
                    json_matches = re.search(json_pattern, raw_text)
                    
                    if json_matches:
                        json_str = json_matches.group(1)
                        try:
                            analysis_result = json.loads(json_str)
                            print("--- Analysis successful with JSON extraction ---")
                            
                            # Validate required keys exist
                            self._validate_and_fix_keys(analysis_result)
                            analysis_result['error'] = None
                            return analysis_result
                        except json.JSONDecodeError as je:
                            print(f"--- Failed to parse extracted JSON: {je} ---")
                
                # If all JSON parsing attempts fail, try to extract data in a more forgiving way
                print("--- Attempting to extract data from non-JSON response ---")
                return self._extract_data_from_text(raw_text, query_context)
                
            except Exception as e:
                print(f"--- Analysis processing error: {e} ---")
                return self._create_fallback_response(f"Processing error: {e}")

        except Exception as e:
            error_msg = f"LLM generation failed: {e}"
            print(f"--- Analysis failed: {error_msg} ---")
            return self._create_fallback_response(error_msg)
    
    def _validate_and_fix_keys(self, analysis_result):
        """Validate and fix missing keys in the analysis result."""
        required_keys = ['summary', 'key_points', 'relevance_score']
        if not all(k in analysis_result for k in required_keys):
            missing = [k for k in required_keys if k not in analysis_result]
            print(f"--- JSON missing required keys: {missing} ---")
            # Add missing keys with default values
            for key in missing:
                if key == 'summary':
                    analysis_result[key] = "Content related to query but missing details"
                elif key == 'key_points':
                    analysis_result[key] = ["Information extracted from webpage"]
                elif key == 'relevance_score':
                    analysis_result[key] = 0.5
        
        # Ensure relevance_score is a float
        if 'relevance_score' in analysis_result and not isinstance(analysis_result['relevance_score'], float):
            try:
                analysis_result['relevance_score'] = float(analysis_result['relevance_score'])
            except (ValueError, TypeError):
                analysis_result['relevance_score'] = 0.5
        
        # Ensure key_points is a list
        if 'key_points' in analysis_result and not isinstance(analysis_result['key_points'], list):
            if isinstance(analysis_result['key_points'], str):
                analysis_result['key_points'] = [analysis_result['key_points']]
            else:
                analysis_result['key_points'] = ["Information extracted from webpage"]
    
    def _extract_data_from_text(self, text: str, query_context: str) -> dict:
        """Extract structured data from unstructured text response."""
        result = {
            'summary': '',
            'key_points': [],
            'relevance_score': 0.3,  # Default to low-moderate relevance
            'error': None
        }
        
        # Try to find a summary (look for paragraphs or sentences after "summary" word)
        summary_patterns = [
            r'["\']?summary["\']?\s*:\s*["\']([^"\']+)["\']',  # "summary": "text"
            r'summary\s*(?:is|:)\s*([^\.]+\.)',  # Summary is: text. or Summary: text.
            r'([^\.]{20,200}\.)'  # Just grab the first substantial sentence as a fallback
        ]
        
        for pattern in summary_patterns:
            summary_match = re.search(pattern, text, re.IGNORECASE)
            if summary_match:
                result['summary'] = summary_match.group(1).strip()
                break
        
        # Try to find key points (look for bullet points, numbered lists, or "key points" sections)
        key_points_patterns = [
            r'["\']?key_points["\']?\s*:\s*\[(.*?)\]',  # "key_points": ["point1", "point2"]
            r'(?:key\s*points|main\s*points|key\s*takeaways)(?:\s*:|\s*are\s*:)(.*?)(?:\n\n|\Z)',  # Key points: text
            r'[-•*]\s*([^\n]+)'  # Bullet points: - Point text or • Point text or * Point text
        ]
        
        for pattern in key_points_patterns:
            if pattern.startswith('[-•*]'):
                # Handle bullet point pattern specially
                bullet_matches = re.findall(pattern, text)
                if bullet_matches and len(bullet_matches) >= 2:  # At least 2 bullet points to consider it a list
                    result['key_points'] = [point.strip() for point in bullet_matches[:5]]  # Limit to 5 points
                    break
            else:
                points_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if points_match:
                    points_text = points_match.group(1).strip()
                    # Split by commas, quotes, or new lines
                    points = re.split(r'[,"\'\n]+', points_text)
                    result['key_points'] = [point.strip() for point in points if point.strip()][:5]
                    break
        
        # If we couldn't extract key points, create some basic ones
        if not result['key_points'] and result['summary']:
            result['key_points'] = ["Information related to " + query_context]
        
        # Try to find relevance score (look for numbers between 0 and 1)
        relevance_patterns = [
            r'["\']?relevance_score["\']?\s*:\s*(0?\.[0-9]+)',  # "relevance_score": 0.7
            r'relevance\s*(?:score|rating|is)\s*:?\s*(0?\.[0-9]+)',  # Relevance score: 0.7
            r'(0?\.[0-9]+)(?:\s*out of\s*1)?'  # Just a decimal like 0.7 or 0.7 out of 1
        ]
        
        for pattern in relevance_patterns:
            relevance_match = re.search(pattern, text, re.IGNORECASE)
            if relevance_match:
                try:
                    score = float(relevance_match.group(1))
                    if 0 <= score <= 1:
                        result['relevance_score'] = score
                        break
                except ValueError:
                    continue
        
        # Determine relevance based on content analysis if no explicit score was found
        if result['summary'] and not result['key_points']:
            # Some summary but no key points = low relevance
            result['relevance_score'] = 0.2
        elif not result['summary'] and result['key_points']:
            # No summary but some key points = low-moderate relevance
            result['relevance_score'] = 0.3
        elif result['summary'] and result['key_points']:
            # Both summary and key points = moderate relevance at minimum
            result['relevance_score'] = max(0.5, result['relevance_score'])
        
        return result
    
    def _create_fallback_response(self, error_msg: str) -> dict:
        """Create a fallback response when analysis fails."""
        return {
            'summary': '',
            'key_points': [],
            'relevance_score': 0.1,  # Very low relevance for failed analyses
            'error': error_msg
        }
    
    def _extract_keywords(self, query: str) -> list:
        """Extract important keywords from the query to aid relevance determination."""
        # Simple keyword extraction - remove common words and keep substantive terms
        common_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 
            'when', 'where', 'how', 'why', 'who', 'whom', 'which', 'tell', 'me', 
            'about', 'can', 'you', 'please', 'need', 'would', 'could', 'should', 'is', 
            'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
            'does', 'did', 'will', 'shall', 'may', 'might', 'must', 'can', 'current'
        }
        words = query.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        return keywords

# Example usage (for testing - requires API key in .env)
if __name__ == '__main__':
    if not api_key:
        print("Skipping ContentAnalyzerTool test because GEMINI_API_KEY is not set.")
    else:
        analyzer = ContentAnalyzerTool()
        test_content = """
        Python is a versatile language often used in web development.
        Its frameworks like Django and Flask allow for rapid development.
        Benefits include a large standard library, strong community support, and readability.
        However, Python's Global Interpreter Lock (GIL) can limit true parallelism for CPU-bound tasks,
        and it might be slower than compiled languages like Java or C++ for certain operations.
        Data science is another popular application area for Python.
        """
        test_query = "Pros and cons of Python for web development"

        analysis = analyzer.analyze(test_content, test_query)

        print("\n--- Analysis Result ---")
        if analysis.get('error'):
            print(f"Error: {analysis['error']}")
        else:
            print(f"Relevance Score: {analysis.get('relevance_score')}")
            print(f"Summary: {analysis.get('summary')}")
            print("Key Points:")
            for point in analysis.get('key_points', []):
                print(f"- {point}") 