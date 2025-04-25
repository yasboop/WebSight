# WebSight Troubleshooting Guide

This guide covers common issues you might encounter while using or deploying WebSight, along with their solutions.

## Table of Contents
- [Installation Issues](#installation-issues)
- [API Key Problems](#api-key-problems)
- [Application Startup Issues](#application-startup-issues)
- [Search Functionality Issues](#search-functionality-issues)
- [Display and UI Issues](#display-and-ui-issues)
- [Docker Deployment Issues](#docker-deployment-issues)
- [Performance Problems](#performance-problems)

## Installation Issues

### Dependencies Installation Fails

**Problem**: You see errors when running `pip install -r requirements.txt`

**Solutions**:
1. Ensure you're using Python 3.9 or higher:
   ```
   python --version
   ```

2. Try creating a fresh virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. If specific packages fail, try installing them individually:
   ```
   pip install [problematic-package]
   ```

### Conflicting Dependencies

**Problem**: You see warnings about conflicting package versions

**Solution**:
```
pip install --upgrade -r requirements.txt --force-reinstall
```

## API Key Problems

### Google Gemini API Key Issues

**Problem**: You see errors about invalid or missing Gemini API key

**Solutions**:
1. Verify your API key is correctly set in the `.env` file:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

2. Check that your API key is active in the Google AI Studio dashboard

3. Ensure the API key has access to the Gemini model you're trying to use

4. Try setting the API key directly in your environment:
   ```
   export GOOGLE_API_KEY=your_actual_api_key_here  # On Windows: set GOOGLE_API_KEY=your_actual_api_key_here
   ```

### DuckDuckGo Search API Issues

**Problem**: Search results aren't being returned or you see search-related errors

**Solutions**:
1. Check your internet connection

2. Verify the search module is working by running a test:
   ```python
   from tools.search_tool import perform_search
   results = perform_search("test query")
   print(results)
   ```

3. DuckDuckGo may be blocking requests. Try adding a delay between searches by editing the search tool.

## Application Startup Issues

### Port Already in Use

**Problem**: You see "Address already in use" when starting the application

**Solutions**:
1. Find and stop the process using the port:
   ```
   # For macOS/Linux
   lsof -i :5001
   kill -9 [PID]
   
   # For Windows
   netstat -ano | findstr :5001
   taskkill /PID [PID] /F
   ```

2. Use a different port:
   ```
   export PORT=5002  # On Windows: set PORT=5002
   python app.py
   ```

### Flask Application Won't Start

**Problem**: The application crashes on startup with various errors

**Solutions**:
1. Check for syntax errors in your Python files

2. Ensure all required environment variables are set:
   ```
   GOOGLE_API_KEY=your_api_key
   PORT=5001  # or another free port
   ```

3. Check the application logs for specific error messages:
   ```
   python app.py 2> error.log
   ```

## Search Functionality Issues

### No Results Returned

**Problem**: Your research query returns no results

**Solutions**:
1. Try a simpler query

2. Check your internet connection

3. Verify the search tool is working correctly:
   ```python
   from tools.search_tool import perform_search
   results = perform_search("current news")
   print(results)
   ```

4. Check if DuckDuckGo is accessible from your network (some networks may block it)

### Irrelevant Search Results

**Problem**: The search results don't match your query

**Solutions**:
1. Be more specific in your query

2. Try adding specific keywords or quotes

3. For technical topics, include specific terminology

### "Too Many Requests" Error

**Problem**: You see rate limit errors in the logs

**Solution**:
Implement a delay between searches by adding time.sleep() in the search tool

## Display and UI Issues

### Results Not Displaying

**Problem**: Research completes but no results appear on screen

**Solutions**:
1. Check the browser console for JavaScript errors:
   - Right-click on the page
   - Select "Inspect" or "Inspect Element"
   - Go to the "Console" tab

2. Try clearing your browser cache and reload the page

3. Check if the results div is actually receiving content (it might be hidden):
   ```javascript
   // In browser console
   document.getElementById('result-section').innerHTML
   ```

### Page Layout Issues

**Problem**: The WebSight UI appears broken or misaligned

**Solutions**:
1. Try a different browser (Chrome usually has the best compatibility)

2. Clear your browser cache and reload

3. Check if your browser has JavaScript enabled

4. Make sure you're using a supported browser version

## Docker Deployment Issues

### Docker Build Fails

**Problem**: `docker build` command fails with errors

**Solutions**:
1. Ensure Docker is properly installed and running:
   ```
   docker --version
   ```

2. Check for syntax errors in your Dockerfile

3. Try rebuilding with no cache:
   ```
   docker build --no-cache -t websight .
   ```

4. Make sure you have internet access to pull base images

### Container Starts But Application is Inaccessible

**Problem**: Docker container starts successfully but you can't access the application

**Solutions**:
1. Verify the container is running:
   ```
   docker ps
   ```

2. Check container logs:
   ```
   docker logs [container_id]
   ```

3. Ensure the port mapping is correct:
   ```
   docker run -p 5001:5001 --env-file .env websight
   ```

4. Try accessing with the correct port: http://localhost:5001

## Performance Problems

### Slow Response Times

**Problem**: Research queries take too long to complete

**Solutions**:
1. Use more specific queries to focus the search

2. Check your internet connection speed

3. Adjust the maximum number of sources processed:
   - In `agent/research_agent.py`, reduce the number of sources that get processed

4. Try running WebSight on a more powerful machine

### High Memory Usage

**Problem**: The WebSight process uses excessive memory

**Solutions**:
1. Limit the number of sources processed per query

2. Avoid multiple complex queries in quick succession

3. Restart the Flask application periodically

4. If using Docker, add memory limits:
   ```
   docker run -p 5001:5001 --memory=1g --env-file .env websight
   ```

### Browser Becomes Unresponsive

**Problem**: Browser slows down or crashes when using WebSight

**Solutions**:
1. Try clearing your browser cache and cookies

2. Reload the page between research sessions

3. Use a more lightweight browser

4. Avoid having multiple research queries running simultaneously

## Advanced Troubleshooting

If you're experiencing persistent issues:

1. Enable debug logging:
   ```python
   # Add to app.py
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Check application logs:
   ```
   python app.py > app.log 2>&1
   ```

3. Isolate components for testing:
   ```python
   # Test the AI component
   from agent.ai_agent import generate_response
   result = generate_response("Sample prompt", "sample content")
   print(result)
   ```

4. Create a minimal reproduction case to isolate the issue

5. Check GitHub issues to see if it's a known problem

## Getting Additional Help

If you're still experiencing issues:

1. File an issue on GitHub with:
   - Detailed description of the problem
   - Steps to reproduce
   - Your environment details (OS, Python version, browser)
   - Relevant logs or error messages

2. Consider reaching out to the community in the discussions section

3. For API-specific issues, consult the relevant service documentation:
   - [Google Gemini API Documentation](https://ai.google.dev/docs)
   - [DuckDuckGo API Documentation](https://duckduckgo.com/api) 