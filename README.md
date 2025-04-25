# WebSight: AI-Powered Web Research Assistant

![WebSight Logo](static/img/websight-logo.png)

WebSight is an advanced AI-powered web research assistant that helps you find, analyze, and synthesize information from the web. It uses Google's Gemini API to provide comprehensive answers to your research questions by analyzing multiple sources and delivering curated, contextual information.

## Features

- **Powerful Research Capabilities**: Ask complex questions and get comprehensive answers synthesized from multiple web sources
- **Visual Research Process**: See exactly how WebSight analyzes and processes information in real-time
- **Context-Aware Responses**: WebSight maintains conversation context, remembering previous queries for more relevant follow-up answers
- **Source Attribution**: All information is properly cited with links to original sources
- **User-Friendly Interface**: Clean, intuitive UI inspired by modern research tools
- **Mobile-Responsive Design**: Works seamlessly across desktop and mobile devices


## Live Demo

Try WebSight now: [https://websight-928850085859.us-central1.run.app](https://websight-928850085859.us-central1.run.app)

## Screenshot

![WebSight Screenshot](static/img/websight-screenshot.png)

## Installation

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key from [Google AI Studio](https://ai.google.dev/)

### Local Installation

1. Clone the repository:
   ```
   git clone https://github.com/yasboop/WebSight.git
   cd websight
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   PORT=5001
   ```

5. Start the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5001
   ```

### Docker Installation

1. Build the Docker image:
   ```
   docker build -t websight .
   ```

2. Run the container:
   ```
   docker run -p 5001:5001 --env-file .env websight
   ```

3. Access WebSight at:
   ```
   http://localhost:5001
   ```

## Using WebSight

1. Enter your research question in the search box
2. Click the "Research" button or press Enter
3. Watch as WebSight:
   - Analyzes your query
   - Searches for relevant information
   - Extracts content from web pages
   - Analyzes the content
   - Synthesizes a comprehensive answer
4. Review the answer and cited sources
5. Ask follow-up questions that build on previous context

### Example Queries

- "What are the latest advancements in renewable energy storage?"
- "Explain quantum computing in simple terms"
- "How does Python compare to JavaScript for web development?"
- "What are the current economic impacts of climate change?"

## Architecture

WebSight follows a modular architecture with these key components:

- **Web Interface**: Flask-based frontend with responsive design
- **Research Agent**: Coordinates the research process using specialized tools
- **AI Integration**: Leverages Google's Gemini API for natural language processing
- **Search Tools**: Uses DuckDuckGo for privacy-focused web searches
- **Content Extraction**: Retrieves and parses relevant content from web pages
- **Session Management**: Maintains conversation context between queries

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Design Decisions

WebSight's design prioritizes:

- **Transparency**: Making the research process visible and understandable
- **Privacy**: Using privacy-respecting search APIs
- **Modularity**: Facilitating easy extension and maintenance
- **User Experience**: Creating an intuitive, responsive interface

For more information on design rationales, see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).

## Troubleshooting

If you encounter issues, please refer to our [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide for solutions to common problems.

## Development

### Running Tests

```
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini API for natural language processing
- DuckDuckGo Search API for web queries
- Flask and its community for the web framework
- All open-source libraries that made this project possible

## Contact

- GitHub: [yasboop](https://github.com/yourusername)
- Email: your.email@example.com 