# WebSight Demo Script

## Introduction (0:00-0:30)

Hello everyone! Today Im excited to show you WebSight, an AI-powered web research assistant that I developed to help users find, analyze, and synthesize information from across the web.

## Project Overview (0:30-1:30)

WebSight is designed to transform the way we research topics online. Instead of jumping between multiple search results and manually comparing information, WebSight does the heavy lifting for you.

Key features include:
- Powerful research capabilities using Google Gemini API
- Visual research process that shows exactly how information is being gathered and analyzed
- Context-aware responses that remember your previous queries
- Source attribution with direct links to all information sources
- Clean, modern UI inspired by tools like Perplexity

Unlike basic search engines, WebSight actually reads and analyzes the content from multiple sources, synthesizing a comprehensive answer that cites all sources used.

## Technical Architecture (1:30-3:00)

WebSight is built with a modular architecture that includes:

1. **Web Interface**: A Flask-based frontend with responsive design
2. **Research Agent**: The core component that coordinates the research process
3. **Tool Integration**: Specialized tools for searching, scraping, and analyzing content
4. **AI Processing**: Google Gemini AI for understanding queries and synthesizing answers

The system follows a research process that includes:
- Query Analysis: Understanding what the user is asking
- Web Search: Finding relevant sources using DuckDuckGo
- Content Extraction: Parsing content from web pages
- Content Analysis: Evaluating relevance and quality
- Information Synthesis: Creating a comprehensive answer

One of the key technical achievements is the real-time progress visualization, which gives users transparency into the research process.

## Live Demo (3:00-5:00)

Lets see WebSight in action. Here Im going to research "current terrorism scene in India" as an example query.

As you can see, when I submit this query:
1. WebSight begins by analyzing what Im asking
2. It then searches across the web for relevant information
3. It extracts content from multiple sources, including CNN, NDTV, and other news sites
4. It analyzes the content from each source to determine relevance
5. Finally, it synthesizes a comprehensive answer that includes citations

Notice how the interface updates in real-time, showing each step of the process. This transparency is a key design principle for WebSight.

Lets try another question to demonstrate the context awareness...

## Deployment and Future Work (5:00-6:00)

WebSight is currently deployed on Google Cloud Run, making it accessible from anywhere with an internet connection. The entire application is containerized with Docker for easy deployment and scaling.

For future development, Im planning to add:
- Enhanced source validation for better fact-checking
- Custom search indexing for specialized knowledge domains
- User accounts for persistent research history
- Mobile application for on-the-go research

## Conclusion (6:00-6:30)

WebSight represents a step forward in making web research more efficient and transparent. By combining AI with traditional web search, it delivers a superior research experience that saves time and provides more comprehensive results.

Thank you for watching! The code is available on GitHub at github.com/yasboop/WebSight, and you can try out the application at the URL shown on screen.
