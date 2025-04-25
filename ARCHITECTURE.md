# WebSight Architecture

This document outlines the architectural design of WebSight, an AI-powered web research assistant.

## System Overview

WebSight is designed as a modular system with several interconnected components that work together to process research queries, search for information across the web, analyze content, and synthesize comprehensive answers.

![Architecture Diagram](https://via.placeholder.com/800x600.png?text=WebSight+Architecture+Diagram)

## Core Components

### 1. Web Interface (Flask Application)

The user-facing component built with Flask that handles:
- Receiving user queries
- Managing user sessions and context history
- Displaying research results and process visualization
- Providing a responsive UI for all devices

**Key Files:**
- `app.py`: Main Flask application entry point
- `templates/index.html`: Main HTML template
- `static/css/style.css`: Styling for the application
- `static/js/websight.js`: Frontend JavaScript functionality

### 2. Research Agent

The central orchestrator that coordinates the entire research process:

**Key Components:**
- `agent/researcher.py`: Main research coordinator
- `agent/analyzer.py`: Handles query analysis and result synthesis
- `agent/session_manager.py`: Manages conversational context and history

**Responsibilities:**
- Breaking down complex queries into actionable search strategies
- Determining which tools to use for information gathering
- Managing the overall research workflow
- Maintaining conversation context for follow-up queries
- Synthesizing final answers from multiple sources

### 3. Tool Integration Layer

A collection of specialized tools for gathering and processing information:

**Key Tools:**
- `tools/search.py`: Interface with web search APIs
- `tools/scraper.py`: Extract content from web pages
- `tools/content_analyzer.py`: Analyze and evaluate content relevance

**Capabilities:**
- Performing targeted web searches using DuckDuckGo
- Extracting relevant content from web pages
- Filtering and ranking search results
- Analyzing content quality and relevance

### 4. AI Processing Layer

Leverages Google's Gemini API for advanced language understanding and generation:

**Key Functionality:**
- Query analysis and decomposition
- Content relevance evaluation
- Information synthesis across multiple sources
- Natural language generation for coherent answers

## Data Flow

1. **Query Submission**:
   - User submits a research query through the web interface
   - Query is sent to the Flask backend via a POST request to `/research`

2. **Query Processing**:
   - Flask routes the query to the Research Agent
   - Research Agent analyzes the query using Gemini AI
   - Session history is checked for relevant context

3. **Information Gathering**:
   - Search strategies are formulated based on query analysis
   - Web search is performed using the Search Tool
   - Web pages are scraped for content using the Scraper Tool

4. **Content Analysis**:
   - Retrieved content is analyzed for relevance and quality
   - Most relevant information is extracted and organized

5. **Answer Synthesis**:
   - Gemini AI synthesizes a comprehensive answer from analyzed content
   - Sources are documented with relevance scores
   - Previous conversation context is incorporated if relevant

6. **Result Presentation**:
   - Synthesized answer is returned to the Flask application
   - Results are formatted and displayed to the user
   - Research process visualization is updated in real-time
   - Sources are listed for transparency and verification

## Context Management

WebSight maintains session-based context to improve follow-up queries:

1. **Session Tracking**:
   - Each user session has a unique identifier
   - Up to 10 previous research queries and results are stored

2. **Context Utilization**:
   - New queries are analyzed in relation to previous research
   - Relevant context is incorporated into the research process
   - Search strategies are refined based on conversation history

3. **Memory Management**:
   - Older sessions are automatically pruned
   - Users can manually clear their research history

## API Integration

### Google Gemini API

Used for:
- Natural language understanding
- Query analysis
- Content relevance evaluation
- Information synthesis

### DuckDuckGo Search API

Used for:
- Web search functionality
- Finding relevant sources across the internet

## Scalability Considerations

- **Stateless Design**: The core application is designed to be stateless, facilitating horizontal scaling
- **Caching**: Frequently requested research topics can be cached to improve performance
- **Async Processing**: Long-running research tasks are processed asynchronously
- **Docker Containerization**: Facilitates deployment across different environments

## Security Measures

- **API Key Management**: Secure handling of API keys via environment variables
- **Input Validation**: All user inputs are validated before processing
- **Session Management**: Secure session handling to prevent unauthorized access
- **Content Filtering**: Inappropriate content detection and filtering

## Deployment Architecture

WebSight is designed to be deployed in various environments:

1. **Local Development**:
   - Flask development server
   - Local environment variables

2. **Docker Deployment**:
   - Containerized application
   - Environment variables passed to container

3. **Cloud Deployment (Google Cloud Run)**:
   - Serverless container deployment
   - Auto-scaling based on demand
   - Secrets management for API keys

## Future Architectural Enhancements

1. **Distributed Research Pipeline**:
   - Separate microservices for different research stages
   - Message queue for asynchronous processing

2. **Enhanced Caching Layer**:
   - Redis cache for frequently requested topics
   - Cached search results for common queries

3. **Advanced Source Validation**:
   - Credibility scoring for information sources
   - Cross-reference verification across multiple sources

4. **Custom Search Index**:
   - Building a specialized search index for improved results
   - Domain-specific knowledge bases 