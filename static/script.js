// Global variables
let currentResults = null;

// DOM elements
const searchForm = document.getElementById('searchForm');
const searchButton = document.getElementById('searchButton');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const videosGrid = document.getElementById('videosGrid');
const pdfsGrid = document.getElementById('pdfsGrid');

// Event listeners
if (searchForm) {
    searchForm.addEventListener('submit', handleSearchSubmit);
}

// Handle main search form submission
async function handleSearchSubmit(e) {
    e.preventDefault();
    const topic = document.getElementById('topic').value.trim();
    
    if (!topic) {
        showError('Please enter a topic to search for.');
        return;
    }

    showLoading();
    hideError();
    hideResults();

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic })
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
        } else {
            currentResults = data;
            displayResults(data);
        }
    } catch (error) {
        showError('Failed to connect to the server. Please try again.');
        console.error('Search error:', error);
    } finally {
        hideLoading();
    }
}

// Alternative search handler (for your custom implementation)
function handleSearch() {
    const query = document.getElementById('searchInput')?.value || document.getElementById('topic')?.value;
    const semantic = document.getElementById('semanticInput')?.value || document.getElementById('semanticQuery')?.value;
    
    if (query && query.trim()) {
        const searchQueryElement = document.getElementById('searchQuery');
        if (searchQueryElement) {
            searchQueryElement.textContent = query;
        }
        
        const queryTopicElement = document.getElementById('queryTopic');
        if (queryTopicElement) {
            queryTopicElement.textContent = query;
        }
        
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    } else {
        alert('Please enter a learning topic');
    }
}

// Enter key listener for search input
const searchInput = document.getElementById('searchInput') || document.getElementById('topic');
if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSearch();
        }
    });
}

// Display search results
function displayResults(data) {
    const queryTopicElement = document.getElementById('queryTopic');
    if (queryTopicElement) {
        queryTopicElement.textContent = data.topic;
    }

    // Display videos
    if (videosGrid) {
        if (data.videos && data.videos.length > 0) {
            videosGrid.innerHTML = data.videos.map(video => `
                <div class="result-card">
                    <div class="card-header video-header">
                        <div class="video-thumb">▶</div>
                        <span class="card-badge">Video</span>
                    </div>
                    <div class="card-body">
                        <h4 class="card-title">${video.title}</h4>
                        <p class="card-desc">${video.description || 'Comprehensive video covering key concepts.'}</p>
                        <div class="card-meta">
                            <span class="meta-item">Channel: ${video.channel || 'Google Developers'}</span>
                        </div>
                        <a href="${video.url}" target="_blank" class="card-link">Watch Video →</a>
                    </div>
                </div>
            `).join('');
        } else {
            videosGrid.innerHTML = '<p class="no-results">No videos found.</p>';
        }
    }

    // Display PDFs
    if (pdfsGrid) {
        if (data.pdfs && data.pdfs.length > 0) {
            pdfsGrid.innerHTML = data.pdfs.map(pdf => `
                <div class="result-card">
                    <div class="card-header paper-header">
                        <div class="paper-icon">📄</div>
                        <span class="card-badge">Paper</span>
                    </div>
                    <div class="card-body">
                        <h4 class="card-title">${pdf.title}</h4>
                        <p class="card-desc">${pdf.summary || 'Foundational text on key concepts and algorithms.'}</p>
                        <div class="card-meta">
                            <span class="meta-item">Authors: ${pdf.authors ? pdf.authors.slice(0,2).join(', ') : 'Christopher Bishop'}</span>
                            ${pdf.year ? `<span class="meta-item">${pdf.year}</span>` : ''}
                            ${pdf.citationCount ? `<span class="meta-item">📊 ${pdf.citationCount} citations</span>` : ''}
                        </div>
                        <a href="${pdf.pdf_url}" target="_blank" class="card-link">Read Paper →</a>
                    </div>
                </div>
            `).join('');
        } else {
            pdfsGrid.innerHTML = '<p class="no-results">No research papers found.</p>';
        }
    }

    showResults();
}

// UI helper functions
function showLoading() {
    if (loadingSection) {
        loadingSection.style.display = 'block';
    }
    if (searchButton) {
        searchButton.disabled = true;
        searchButton.textContent = '⏳ Searching...';
    }
}

function hideLoading() {
    if (loadingSection) {
        loadingSection.style.display = 'none';
    }
    if (searchButton) {
        searchButton.disabled = false;
        searchButton.textContent = '🔍 Find Resources';
    }
}

function showResults() {
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
}

function hideResults() {
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
}

function showError(message) {
    if (errorSection) {
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        errorSection.style.display = 'block';
    }
}

function hideError() {
    if (errorSection) {
        errorSection.style.display = 'none';
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Learning Agent initialized');
});
