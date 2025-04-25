import pytest
import os
from unittest.mock import patch, MagicMock

# Conditionally import the agent only if the API key might be present
# This avoids errors during test collection if the key is missing
agent_module = None
api_key_present = bool(os.getenv("GEMINI_API_KEY"))

if api_key_present:
    try:
        from agent.agent import WebResearchAgent
        agent_module = WebResearchAgent
    except ImportError as e:
        print(f"Could not import WebResearchAgent: {e}")
    except ValueError as e: # Catch initialization errors too
        print(f"Could not initialize WebResearchAgent: {e}")
else:
    print("Skipping agent import for tests as GEMINI_API_KEY is not set.")

# --- Fixtures --- 

@pytest.fixture
def mock_env(monkeypatch):
    """Temporarily sets the API key environment variable for testing."""
    # Use a dummy key for tests that need the variable present but don't call the API
    monkeypatch.setenv("GEMINI_API_KEY", "DUMMY_API_KEY_FOR_TESTING")

@pytest.fixture
def mock_search_tool():
    """Mocks the WebSearchTool."""
    mock = MagicMock()
    mock.search.return_value = [
        {'title': 'Test Result 1', 'url': 'http://example.com/1', 'snippet': 'Snippet 1'},
        {'title': 'Test Result 2', 'url': 'http://example.com/2', 'snippet': 'Snippet 2'}
    ]
    return mock

@pytest.fixture
def mock_scraper_tool():
    """Mocks the WebScraperTool."""
    mock = MagicMock()
    # Simulate scraping success for specific URLs
    def scrape_side_effect(url, timeout=10):
        if url == 'http://example.com/1':
            return {'url': url, 'raw_text': 'Content from page 1 about apples.', 'error': None}
        elif url == 'http://example.com/2':
            return {'url': url, 'raw_text': 'Content from page 2 about oranges.', 'error': None}
        else:
            return {'url': url, 'raw_text': None, 'error': 'Mock scrape failed'}
    mock.scrape.side_effect = scrape_side_effect
    return mock

@pytest.fixture
def mock_analyzer_tool():
    """Mocks the ContentAnalyzerTool."""
    mock = MagicMock()
    def analyze_side_effect(content, query_context):
        if "apples" in content:
            return {'summary': 'Info about apples.', 'key_points': ['Apples are fruit'], 'relevance_score': 0.9, 'error': None}
        elif "oranges" in content:
            return {'summary': 'Info about oranges.', 'key_points': ['Oranges are citrus'], 'relevance_score': 0.8, 'error': None}
        else:
             return {'summary': '', 'key_points': [], 'relevance_score': 0.1, 'error': None}
    mock.analyze.side_effect = analyze_side_effect
    return mock

@pytest.fixture
def mock_llm_model():
    """Mocks the generative model used directly by the agent."""
    mock = MagicMock()
    # Mock responses for query analysis and synthesis
    def generate_content_side_effect(prompt):
        response_mock = MagicMock()
        if "Analyze the following research query" in prompt:
            response_mock.text = '{"analysis": "Mock analysis", "search_query": "mock search keywords"}'
        elif "Based *only* on the provided context" in prompt:
            response_mock.text = "Synthesized mock report based on context."
        else:
            response_mock.text = "Generic mock LLM response."
        return response_mock
    mock.generate_content.side_effect = generate_content_side_effect
    return mock

# --- Tests --- 

# Mark tests that require the agent class (and thus API key potentially)
@pytest.mark.skipif(not agent_module, reason="Agent module could not be loaded, check GEMINI_API_KEY")
@patch('agent.agent.genai.GenerativeModel') # Patch the LLM model inside the agent
@patch('agent.agent.WebSearchTool')
@patch('agent.agent.WebScraperTool')
@patch('agent.agent.ContentAnalyzerTool') # Also patch the analyzer tool instantiation
def test_agent_research_flow(
    MockContentAnalyzerTool, MockWebScraperTool, MockWebSearchTool, MockGenerativeModel,
    mock_env, mock_search_tool, mock_scraper_tool, mock_analyzer_tool, mock_llm_model
):
    """Tests the basic research flow with mocked tools and LLM."""
    # Configure mocks
    MockGenerativeModel.return_value = mock_llm_model
    MockWebSearchTool.return_value = mock_search_tool
    MockWebScraperTool.return_value = mock_scraper_tool
    MockContentAnalyzerTool.return_value = mock_analyzer_tool 
    
    # Instantiate the agent (it will use the mocked tools/model)
    agent = WebResearchAgent()

    test_query = "Tell me about apples"
    report = agent.research(test_query)

    # Assertions (verify mocks were called and report looks reasonable)
    mock_llm_model.generate_content.assert_any_call(pytest.approx(
        f'''Analyze the following research query and identify the core intent and key entities.
        Based on this, suggest a concise, effective search query (max 5 keywords) to use on a web search engine.

        Research Query: "{test_query}"

        Output ONLY a JSON object with the following structure:
        {{
          "analysis": "Brief analysis of the user's intent.",
          "search_query": "Suggested search keywords."
        }}
        '''
    )) # Check analysis prompt
    mock_search_tool.search.assert_called_once_with("mock search keywords", num_results=agent.max_search_results)
    mock_scraper_tool.scrape.assert_any_call('http://example.com/1')
    mock_scraper_tool.scrape.assert_any_call('http://example.com/2')
    mock_analyzer_tool.analyze.assert_any_call('Content from page 1 about apples.', test_query)
    mock_analyzer_tool.analyze.assert_any_call('Content from page 2 about oranges.', test_query)
    
    # Check that synthesis prompt includes expected elements
    synthesis_prompt_call = [call for call in mock_llm_model.generate_content.call_args_list if "Based *only* on the provided context" in call.args[0]]
    assert len(synthesis_prompt_call) == 1
    synthesis_prompt = synthesis_prompt_call[0].args[0]
    assert "Research Query: Tell me about apples" in synthesis_prompt
    assert "Source 1 (URL: http://example.com/1)" in synthesis_prompt
    assert "Summary: Info about apples." in synthesis_prompt
    assert "- Apples are fruit" in synthesis_prompt
    assert "Source 2 (URL: http://example.com/2)" in synthesis_prompt # Assuming it was relevant enough
    assert "Summary: Info about oranges." in synthesis_prompt

    assert report == "Synthesized mock report based on context."

@pytest.mark.skipif(not agent_module, reason="Agent module could not be loaded, check GEMINI_API_KEY")
@patch('agent.agent.genai.GenerativeModel')
@patch('agent.agent.WebSearchTool')
@patch('agent.agent.WebScraperTool')
@patch('agent.agent.ContentAnalyzerTool')
def test_agent_no_search_results(
    MockContentAnalyzerTool, MockWebScraperTool, MockWebSearchTool, MockGenerativeModel,
    mock_env, mock_search_tool, mock_scraper_tool, mock_analyzer_tool, mock_llm_model
):
    """Tests the case where the search tool returns no results."""
    # Configure mocks
    MockGenerativeModel.return_value = mock_llm_model
    mock_search_tool.search.return_value = [] # No results
    MockWebSearchTool.return_value = mock_search_tool
    MockWebScraperTool.return_value = mock_scraper_tool
    MockContentAnalyzerTool.return_value = mock_analyzer_tool 

    agent = WebResearchAgent()
    report = agent.research("Query leading to no results")

    mock_search_tool.search.assert_called_once()
    mock_scraper_tool.scrape.assert_not_called()
    mock_analyzer_tool.analyze.assert_not_called()
    assert "Could not find any relevant web pages" in report

# Add more tests:
# - Test case where scraping fails for all URLs
# - Test case where analysis deems all content irrelevant
# - Test case where LLM calls fail (e.g., query analysis or synthesis)
# - Test handling of different max_sources_to_process values
# - Unit tests for individual tool wrappers if they had more complex logic 