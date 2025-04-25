import os
import json
import time
import uuid
import threading
import logging
from flask import Flask, request, render_template, jsonify, Response, stream_with_context, session
from dotenv import load_dotenv
from queue import Queue
from threading import Thread
from agent.agent import WebResearchAgent
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get API key from environment variable (making sure it's secure for deployment)
# First try using the GEMINI_API_KEY which our agent expects
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    # Try the GOOGLE_AI_API_KEY as a fallback
    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if not api_key:
        # Fallback to .env file for local development
        load_dotenv()
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            raise ValueError("Missing API key (GEMINI_API_KEY or GOOGLE_AI_API_KEY)")

# Set the correct environment variable that the agent expects
os.environ['GEMINI_API_KEY'] = api_key

# Initialize research agent
agent_instance = None
initialization_error = None
research_progress = {}
conversation_history = {}

# Check if API key is present before attempting to initialize the agent
api_key_present = bool(api_key)

if api_key_present:
    try:
        # Import the agent class only if the key is present
        agent_instance = WebResearchAgent()
        print("Web Research Agent initialized successfully.")
    except Exception as e:
        initialization_error = f"Failed to initialize Web Research Agent: {e}"
        print(f"Error: {initialization_error}")
else:
    initialization_error = "API key not found in environment variables. Agent cannot be initialized."
    print(f"Error: {initialization_error}")

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())  # For session management
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def index():
    """Renders the main HTML page."""
    # Create session if it doesn't exist
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        conversation_history[session['user_id']] = []
        
    return render_template('index.html', error=initialization_error)

def run_research_task(query, session_id, user_id, context):
    """Run research in a separate thread and track progress."""
    global research_progress
    try:
        # Initial state
        research_progress[session_id] = {
            "status": "starting",
            "phase": "initialization",
            "message": "Starting research process...",
            "sources": [],
            "progress_pct": 5,
            "result": None,
            "error": None
        }
        
        # Hook into different stages of the research process
        def query_analysis_callback(analysis):
            research_progress[session_id]["status"] = "analyzing_query"
            research_progress[session_id]["phase"] = "query_analysis"
            research_progress[session_id]["message"] = f"Analyzing query: '{query}'"
            research_progress[session_id]["progress_pct"] = 10
            
        def search_callback(search_results):
            research_progress[session_id]["status"] = "searching"
            research_progress[session_id]["phase"] = "web_search"
            research_progress[session_id]["message"] = f"Searching the web for relevant information..."
            research_progress[session_id]["progress_pct"] = 20
        
        def source_callback(source_num, total_sources, url, title, status):
            if status == "start":
                research_progress[session_id]["status"] = "processing_sources"
                research_progress[session_id]["phase"] = "analyzing_content"
                research_progress[session_id]["message"] = f"Analyzing source {source_num}/{total_sources}: {title}"
                # Calculate progress based on how many sources we've processed
                progress_pct = 20 + (source_num / total_sources) * 60
                research_progress[session_id]["progress_pct"] = min(80, progress_pct)
                
                # Add source to the list
                research_progress[session_id]["sources"].append({
                    "url": url,
                    "title": title,
                    "status": "processing",
                    "relevance": None
                })
            elif status == "complete":
                # Update source status and relevance
                for source in research_progress[session_id]["sources"]:
                    if source["url"] == url:
                        source["status"] = "analyzed"
                        source["relevance"] = research_progress[session_id].get("current_relevance", 0.0)
        
        def synthesis_callback():
            research_progress[session_id]["status"] = "synthesizing"
            research_progress[session_id]["phase"] = "synthesis"
            research_progress[session_id]["message"] = "Synthesizing findings into a comprehensive report..."
            research_progress[session_id]["progress_pct"] = 85
        
        # Use context-aware research if we have context
        if context:
            # Include context in the query
            context_text = "Previous research:\n" + "\n".join([
                f"Query: {item['query']}\nSummary: {item['summary']}"
                for item in context if 'summary' in item
            ])
            
            # Modify the query to include context
            augmented_query = f"{query}\n\nContext from previous research: {context_text}"
            result = agent_instance.research_with_context(
                query=query,
                context=context_text,
                query_analysis_callback=query_analysis_callback,
                search_callback=search_callback,
                source_callback=source_callback,
                synthesis_callback=synthesis_callback
            )
        else:
            # If no context, use regular research
            result = agent_instance.research(
                query, 
                query_analysis_callback=query_analysis_callback,
                search_callback=search_callback,
                source_callback=source_callback,
                synthesis_callback=synthesis_callback
            )
        
        # Update final state
        research_progress[session_id]["status"] = "complete"
        research_progress[session_id]["progress_pct"] = 100
        research_progress[session_id]["message"] = "Research complete"
        research_progress[session_id]["result"] = result
        
        # Store in conversation history
        if user_id in conversation_history:
            # Extract a summary for context (first 200 chars)
            summary = result[:200] + "..." if len(result) > 200 else result
            conversation_history[user_id].append({
                "query": query,
                "summary": summary,
                "timestamp": time.time()
            })
            # Keep history to a reasonable size
            if len(conversation_history[user_id]) > 10:
                conversation_history[user_id] = conversation_history[user_id][-10:]
        
    except Exception as e:
        logger.error(f"Research error: {e}", exc_info=True)
        research_progress[session_id]["status"] = "error"
        research_progress[session_id]["error"] = str(e)
        research_progress[session_id]["message"] = f"An error occurred during research: {e}"

@app.route('/research', methods=['POST'])
def research_endpoint():
    """Handles the research query POST request."""
    if not agent_instance:
        return jsonify({"error": initialization_error or "Agent not available."}), 500
    
    query = request.form.get('query')
    if not query:
        return jsonify({"error": "No query provided."}), 400

    try:
        print(f"Received research request for: {query}")
        
        # Get or create user session ID
        user_id = session.get('user_id', str(uuid.uuid4()))
        if 'user_id' not in session:
            session['user_id'] = user_id
            conversation_history[user_id] = []
        
        # Create a unique session ID for this research query
        session_id = f"research_{int(time.time() * 1000)}"
        
        # Get conversation context for this user
        context = []
        if user_id in conversation_history:
            # Get the last 3 conversations for context (can be adjusted)
            context = conversation_history[user_id][-3:]
        
        # Start a thread to run the research
        thread = Thread(target=run_research_task, args=(query, session_id, user_id, context))
        thread.daemon = True
        thread.start()
        
        # Return the session ID for progress tracking
        return jsonify({"session_id": session_id})
    except Exception as e:
        print(f"Error starting research for query '{query}': {e}")
        return jsonify({"error": f"An error occurred starting research: {e}"}), 500

@app.route('/research_progress/<session_id>', methods=['GET'])
def research_progress_endpoint(session_id):
    """Returns the current progress of a research session."""
    if session_id not in research_progress:
        return jsonify({"error": "Invalid session ID"}), 404
    
    return jsonify(research_progress[session_id])

@app.route('/research_stream/<session_id>')
def research_stream(session_id):
    """Stream the research progress as server-sent events."""
    def generate():
        last_progress = None
        
        # Check progress every second until complete or error
        while session_id in research_progress:
            current_progress = research_progress[session_id]
            
            # Only send updates when there's a change
            if current_progress != last_progress:
                last_progress = current_progress.copy()
                yield f"data: {json.dumps(current_progress)}\n\n"
            
            # If research is complete or errored, send one last update and stop
            if current_progress.get("status") in ["complete", "error"]:
                if current_progress.get("status") == "complete" and current_progress.get("result"):
                    # Clean up, but keep session data for 5 minutes for client to fetch the result
                    # We'll use a timer to remove it later
                    def remove_session():
                        if session_id in research_progress:
                            del research_progress[session_id]
                    
                    # Schedule cleanup after 5 minutes
                    cleanup_thread = Thread(target=lambda: (time.sleep(300), remove_session()))
                    cleanup_thread.daemon = True
                    cleanup_thread.start()
                    
                break
            
            time.sleep(1)
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

@app.route('/conversation_history')
def get_conversation_history():
    """Get the conversation history for the current user"""
    user_id = session.get('user_id')
    if not user_id or user_id not in conversation_history:
        return jsonify([])
    
    return jsonify(conversation_history[user_id])

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear the conversation history for the current user"""
    user_id = session.get('user_id')
    if user_id and user_id in conversation_history:
        conversation_history[user_id] = []
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Use environment variable for port, default to 5001 if not set
    port = int(os.environ.get('PORT', 5001))
    # Runs on http://127.0.0.1:5001 by default
    # Use host='0.0.0.0' to make it accessible on your network
    app.run(debug=True, port=port, host='0.0.0.0') 