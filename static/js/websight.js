// WebSight - Advanced AI Research Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchForm = document.getElementById('research-form');
    const queryInput = document.getElementById('query-input');
    const searchButton = document.getElementById('search-button');
    const exampleChips = document.querySelectorAll('.example-chip');
    const resultSection = document.getElementById('result-container');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const resultContent = document.getElementById('result-content');
    const sourcesList = document.getElementById('sources-list');
    const sourcesCount = document.getElementById('sources-count');
    const loadingAnimation = document.querySelector('.loading-animation');
    const researchStatus = document.getElementById('research-status');
    const historyContainer = document.getElementById('history-container');
    const historyItems = document.getElementById('history-items');
    const clearHistoryBtn = document.getElementById('clear-history');
    
    // Research Process Elements
    const researchProcess = document.getElementById('research-process');
    const toggleProcessBtn = document.getElementById('toggle-process');
    const toggleSourcesBtn = document.getElementById('toggle-sources');
    const sourcesPanel = document.getElementById('sources-panel');
    const closeSourcesPanelBtn = document.querySelector('.close-panel');
    
    // Process steps elements
    const queryStep = document.getElementById('step-query');
    const searchStep = document.getElementById('step-search');
    const extractionStep = document.getElementById('step-extraction');
    const analysisStep = document.getElementById('step-analysis');
    const synthesisStep = document.getElementById('step-synthesis');
    
    // Step details elements
    const queryDetails = document.getElementById('query-analysis-details');
    const searchDetails = document.getElementById('search-details');
    const extractionDetails = document.getElementById('extraction-details');
    const analysisDetails = document.getElementById('analysis-details');
    const synthesisDetails = document.getElementById('synthesis-details');
    
    // Feedback section
    const feedbackSection = document.querySelector('.feedback-section');
    const feedbackButtons = document.querySelectorAll('.feedback-btn');

    // Load conversation history on page load
    loadConversationHistory();

    // Toggle research process view
    if (toggleProcessBtn) {
        toggleProcessBtn.addEventListener('click', function() {
            if (researchProcess.style.display === 'none') {
                researchProcess.style.display = 'block';
                toggleProcessBtn.classList.add('active');
            } else {
                researchProcess.style.display = 'none';
                toggleProcessBtn.classList.remove('active');
            }
        });
    }
    
    // Toggle sources panel
    if (toggleSourcesBtn) {
        toggleSourcesBtn.addEventListener('click', function() {
            const resultGrid = document.querySelector('.result-grid');
            if (resultGrid.classList.contains('show-sources')) {
                resultGrid.classList.remove('show-sources');
                toggleSourcesBtn.classList.remove('active');
            } else {
                resultGrid.classList.add('show-sources');
                toggleSourcesBtn.classList.add('active');
            }
        });
    }
    
    // Close sources panel
    if (closeSourcesPanelBtn) {
        closeSourcesPanelBtn.addEventListener('click', function() {
            const resultGrid = document.querySelector('.result-grid');
            resultGrid.classList.remove('show-sources');
            toggleSourcesBtn.classList.remove('active');
        });
    }
    
    // Feedback buttons
    if (feedbackButtons) {
        feedbackButtons.forEach(button => {
            button.addEventListener('click', function() {
                const feedback = this.dataset.feedback;
                // Here you could send feedback to the server
                feedbackSection.innerHTML = '<p>Thank you for your feedback!</p>';
            });
        });
    }

    // Example queries click handler
    exampleChips.forEach(chip => {
        chip.addEventListener('click', function() {
            queryInput.value = this.dataset.query || this.textContent.trim();
            searchForm.dispatchEvent(new Event('submit'));
        });
    });

    // Clear history button
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', function() {
            fetch('/clear_history', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    historyItems.innerHTML = '';
                    historyContainer.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error clearing history:', error);
            });
        });
    }

    // Search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const query = queryInput.value.trim();
            if (!query) return;
            
            // Show result section if hidden
            resultSection.style.display = 'block';
            
            // Reset UI for new search
            resetUI();
            
            // Start search process
            startSearch(query);
            
            // Scroll to results
            resultSection.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Load conversation history
    function loadConversationHistory() {
        fetch('/conversation_history')
            .then(response => response.json())
            .then(history => {
                if (history && history.length > 0) {
                    historyContainer.style.display = 'block';
                    renderHistoryItems(history);
                } else {
                    historyContainer.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error loading conversation history:', error);
                historyContainer.style.display = 'none';
            });
    }

    // Render history items
    function renderHistoryItems(history) {
        historyItems.innerHTML = '';
        
        history.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            // Format timestamp
            const date = new Date(item.timestamp * 1000);
            const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
            
            historyItem.innerHTML = `
                <div class="history-query">
                    <span class="history-index">${index + 1}</span>
                    <span class="history-text">${item.query}</span>
                </div>
                <div class="history-summary">${item.summary}</div>
                <div class="history-time">${formattedDate}</div>
                <button class="history-reuse-btn" data-query="${item.query}">
                    <i class="fas fa-search"></i> Research Again
                </button>
            `;
            
            historyItems.appendChild(historyItem);
        });
        
        // Add click event to the "Research Again" buttons
        document.querySelectorAll('.history-reuse-btn').forEach(button => {
            button.addEventListener('click', function() {
                queryInput.value = this.dataset.query;
                searchForm.dispatchEvent(new Event('submit'));
                
                // Scroll to the search form
                searchForm.scrollIntoView({ behavior: 'smooth' });
            });
        });
    }

    // Reset UI elements for new search
    function resetUI() {
        // Reset progress
        progressFill.style.width = '0%';
        progressText.textContent = 'Starting research...';
        
        // Reset content
        resultContent.innerHTML = '';
        sourcesList.innerHTML = '';
        sourcesCount.textContent = '0';
        
        // Show loading animation
        loadingAnimation.classList.remove('hidden');
        resultContent.classList.add('hidden');
        
        // Hide feedback section
        if (feedbackSection) {
            feedbackSection.classList.add('hidden');
        }
        
        // Update research status
        researchStatus.innerHTML = '<span class="status-icon">⏳</span> Researching...';
        
        // Disable search button during process
        searchButton.disabled = true;
        
        // Show research process and initialize steps
        researchProcess.style.display = 'block';
        toggleProcessBtn.classList.add('active');
        resetProcessSteps();
    }
    
    // Reset research process steps
    function resetProcessSteps() {
        const steps = [queryStep, searchStep, extractionStep, analysisStep, synthesisStep];
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Reset step details
        queryDetails.innerHTML = '<div class="thinking-indicator"><span class="dot-1">.</span><span class="dot-2">.</span><span class="dot-3">.</span></div>';
        searchDetails.innerHTML = '<div class="thinking-indicator"><span class="dot-1">.</span><span class="dot-2">.</span><span class="dot-3">.</span></div>';
        extractionDetails.innerHTML = '<div class="thinking-indicator"><span class="dot-1">.</span><span class="dot-2">.</span><span class="dot-3">.</span></div>';
        analysisDetails.innerHTML = '<div class="thinking-indicator"><span class="dot-1">.</span><span class="dot-2">.</span><span class="dot-3">.</span></div>';
        synthesisDetails.innerHTML = '<div class="thinking-indicator"><span class="dot-1">.</span><span class="dot-2">.</span><span class="dot-3">.</span></div>';
        
        // Activate first step
        queryStep.classList.add('active');
    }

    // Start the search process
    function startSearch(query) {
        // Use fetch to POST the query
        fetch('/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                handleError(data.error);
                return;
            }
            
            // Get the session ID
            const sessionId = data.session_id;
            
            // Start tracking progress
            trackProgress(sessionId);
        })
        .catch(error => {
            console.error('Error starting research:', error);
            handleError('Failed to start research process. Please try again.');
        });
    }
    
    // Track research progress
    function trackProgress(sessionId) {
        const progressSource = new EventSource(`/research_stream/${sessionId}`);
        
        progressSource.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            // Update progress bar
            progressFill.style.width = `${data.progress_pct}%`;
            progressText.textContent = data.message || `Research ${data.progress_pct}% complete`;
            
            // Update process steps based on phase
            updateProcessSteps(data);
            
            // Add sources as they come in
            if (data.sources && data.sources.length > 0) {
                updateSourcesList(data.sources);
            }
            
            // If complete, display result
            if (data.status === 'complete' && data.result) {
                displayResult({content: data.result});
                progressSource.close();
                
                // Refresh history after research completes
                loadConversationHistory();
            }
            
            // If error, display error
            if (data.status === 'error') {
                handleError(data.error);
                progressSource.close();
            }
        };
        
        progressSource.onerror = function() {
            console.error('EventSource error');
            progressSource.close();
            handleError('Connection to server lost. Please try again.');
        };
    }
    
    // Update process steps based on current phase
    function updateProcessSteps(data) {
        const phase = data.phase;
        const progress = data.progress_pct;
        
        if (phase === 'initialization' || phase === 'query_analysis') {
            // Query analysis active
            queryStep.classList.add('active');
            
            if (data.status === 'analyzing_query') {
                queryDetails.innerHTML = `<p>Analyzing: "${data.message || 'Processing your query...'}"</p>`;
            }
        } 
        else if (phase === 'web_search') {
            // Query analysis completed, web search active
            queryStep.classList.remove('active');
            queryStep.classList.add('completed');
            searchStep.classList.add('active');
            
            queryDetails.innerHTML = `<p>Query optimized for search</p>`;
            searchDetails.innerHTML = `<p>${data.message || 'Searching for relevant sources...'}</p>`;
        } 
        else if (phase === 'analyzing_content') {
            // Web search completed, content analysis active
            queryStep.classList.remove('active');
            searchStep.classList.remove('active');
            queryStep.classList.add('completed');
            searchStep.classList.add('completed');
            
            // Alternate between extraction and analysis steps for visual feedback
            if (data.message && data.message.includes('Analyzing source')) {
                extractionStep.classList.remove('active');
                analysisStep.classList.add('active');
                
                searchDetails.innerHTML = `<p>Found ${data.sources.length} potential sources</p>`;
                extractionDetails.innerHTML = `<p>Extracting content from web pages</p>`;
                analysisDetails.innerHTML = `<p>${data.message}</p>`;
            } else {
                extractionStep.classList.add('active');
                analysisStep.classList.remove('active');
                
                extractionDetails.innerHTML = `<p>${data.message || 'Processing web content...'}</p>`;
            }
        } 
        else if (phase === 'synthesis') {
            // Content analysis completed, synthesis active
            queryStep.classList.add('completed');
            searchStep.classList.add('completed');
            extractionStep.classList.add('completed');
            analysisStep.classList.add('completed');
            
            queryStep.classList.remove('active');
            searchStep.classList.remove('active');
            extractionStep.classList.remove('active');
            analysisStep.classList.remove('active');
            
            synthesisStep.classList.add('active');
            
            synthesisDetails.innerHTML = `<p>${data.message || 'Creating comprehensive report...'}</p>`;
        }
        
        if (data.status === 'complete') {
            // All steps completed
            queryStep.classList.add('completed');
            searchStep.classList.add('completed');
            extractionStep.classList.add('completed');
            analysisStep.classList.add('completed');
            synthesisStep.classList.add('completed');
            
            queryStep.classList.remove('active');
            searchStep.classList.remove('active');
            extractionStep.classList.remove('active');
            analysisStep.classList.remove('active');
            synthesisStep.classList.remove('active');
            
            synthesisDetails.innerHTML = `<p>Synthesis complete</p>`;
        }
    }

    // Update sources list
    function updateSourcesList(sources) {
        // Clear existing list
        sourcesList.innerHTML = '';
        
        // Add each source
        sources.forEach((source, index) => {
            if (source.status === 'processing' || source.status === 'analyzed') {
                const sourceItem = document.createElement('li');
                
                // Calculate a relevance score display if available
                let relevanceDisplay = '';
                if (source.relevance && source.relevance > 0) {
                    relevanceDisplay = `<span class="relevance">${(source.relevance * 100).toFixed(0)}% relevant</span>`;
                }
                
                sourceItem.innerHTML = `
                    <div class="source-item">
                        <span class="source-number">${index + 1}</span>
                        <div>
                            <a href="${source.url}" class="source-link" target="_blank" rel="noopener noreferrer">
                                ${source.title || source.url}
                            </a>
                            <span class="source-meta">${new URL(source.url).hostname}</span>
                            ${relevanceDisplay}
                        </div>
                    </div>
                `;
                
                sourcesList.appendChild(sourceItem);
                sourcesCount.textContent = document.querySelectorAll('#sources-list li').length;
            }
        });
    }

    // Display final research result
    function displayResult(data) {
        // Hide loading animation
        loadingAnimation.classList.add('hidden');
        resultContent.classList.remove('hidden');
        
        // Update research status
        researchStatus.innerHTML = '<span class="status-icon">✓</span> Research complete';
        
        // Enable search button
        searchButton.disabled = false;
        
        // Show feedback section
        if (feedbackSection) {
            feedbackSection.classList.remove('hidden');
        }
        
        // Process content
        resultContent.innerHTML = data.content;
        
        // Highlight code blocks if any
        if (window.Prism) {
            Prism.highlightAllUnder(resultContent);
        }
        
        // Auto-show sources panel on mobile
        if (window.innerWidth <= 768) {
            const resultGrid = document.querySelector('.result-grid');
            resultGrid.classList.add('show-sources');
            toggleSourcesBtn.classList.add('active');
        }
    }

    // Handle search errors
    function handleError(errorMsg) {
        // Hide loading animation
        loadingAnimation.classList.add('hidden');
        resultContent.classList.remove('hidden');
        
        // Update research status
        researchStatus.innerHTML = '<span class="status-icon">❌</span> Research failed';
        
        // Enable search button
        searchButton.disabled = false;
        
        // Reset process steps - mark all as failed
        queryStep.classList.remove('active', 'completed');
        searchStep.classList.remove('active', 'completed');
        extractionStep.classList.remove('active', 'completed');
        analysisStep.classList.remove('active', 'completed');
        synthesisStep.classList.remove('active', 'completed');
        
        // Display error message
        resultContent.innerHTML = `
            <div class="error-message">
                <h3>Research Error</h3>
                <p>${errorMsg || 'Sorry, we encountered an error while researching your query. Please try again later or with a different query.'}</p>
            </div>
        `;
    }
}); 