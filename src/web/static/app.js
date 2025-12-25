// API Base URL
const API_BASE = 'http://localhost:8000';

// State management
let currentPlatform = null;
let currentFilters = {
    genre: '',
    minRating: '',
    maxRating: '',
    year: ''
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadPlatforms();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }

    // Filter inputs
    const filterInputs = document.querySelectorAll('.filter-input');
    filterInputs.forEach(input => {
        input.addEventListener('change', applyFilters);
    });

    // Clear filters button
    const clearFiltersBtn = document.getElementById('clearFilters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }
}

// Load available streaming platforms
async function loadPlatforms() {
    try {
        const response = await fetch(`${API_BASE}/api/platforms`);
        const platforms = await response.json();
        
        const platformGrid = document.getElementById('platformGrid');
        platformGrid.innerHTML = platforms.map(platform => `
            <button class="platform-btn" data-platform="${platform}" onclick="selectPlatform('${platform}')">
                ${platform}
            </button>
        `).join('');
    } catch (error) {
        showError('Failed to load streaming platforms');
        console.error(error);
    }
}

// Handle search form submission
async function handleSearch(event) {
    event.preventDefault();
    
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/api/search?query=${encodeURIComponent(query)}&count=20`);
        const data = await response.json();
        
        displayMovies(data.movies, `Search results for "${query}"`);
    } catch (error) {
        showError('Failed to search movies');
        console.error(error);
    }
}

// Select streaming platform
async function selectPlatform(platform) {
    currentPlatform = platform;
    
    // Update UI
    document.querySelectorAll('.platform-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Show filters
    document.getElementById('filters').classList.remove('hidden');
    
    // Load movies
    loadPlatformMovies();
}

// Load movies for selected platform
async function loadPlatformMovies() {
    if (!currentPlatform) return;

    showLoading();
    
    try {
        const params = new URLSearchParams({
            count: 20
        });

        // Add filters if set
        if (currentFilters.genre) params.append('genre', currentFilters.genre);
        if (currentFilters.minRating) params.append('min_rating', currentFilters.minRating);
        if (currentFilters.maxRating) params.append('max_rating', currentFilters.maxRating);
        if (currentFilters.year) params.append('year', currentFilters.year);

        const response = await fetch(`${API_BASE}/api/movies/${encodeURIComponent(currentPlatform)}?${params}`);
        const data = await response.json();
        
        displayMovies(data.movies, `${currentPlatform} Movies`);
    } catch (error) {
        showError('Failed to load platform movies');
        console.error(error);
    }
}

// Apply filters
function applyFilters() {
    currentFilters = {
        genre: document.getElementById('genreFilter').value,
        minRating: document.getElementById('minRatingFilter').value,
        maxRating: document.getElementById('maxRatingFilter').value,
        year: document.getElementById('yearFilter').value
    };

    if (currentPlatform) {
        loadPlatformMovies();
    }
}

// Clear filters
function clearFilters() {
    document.getElementById('genreFilter').value = '';
    document.getElementById('minRatingFilter').value = '';
    document.getElementById('maxRatingFilter').value = '';
    document.getElementById('yearFilter').value = '';
    
    currentFilters = {
        genre: '',
        minRating: '',
        maxRating: '',
        year: ''
    };

    if (currentPlatform) {
        loadPlatformMovies();
    }
}

// Display movies in grid
function displayMovies(movies, title) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsCount = document.getElementById('resultsCount');
    const movieGrid = document.getElementById('movieGrid');

    resultsSection.classList.remove('hidden');
    resultsTitle.textContent = title;
    resultsCount.textContent = `${movies.length} movies found`;

    if (movies.length === 0) {
        movieGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🎬</div>
                <p>No movies found. Try adjusting your filters.</p>
            </div>
        `;
        return;
    }

    movieGrid.innerHTML = movies.map(movie => createMovieCard(movie)).join('');
}

// Create movie card HTML
function createMovieCard(movie) {
    const jwRating = movie.justwatch_rating ? movie.justwatch_rating.toFixed(1) : 'N/A';
    const lbRating = movie.letterboxd_rating ? movie.letterboxd_rating.toFixed(1) : 'N/A';
    const year = movie.year || 'N/A';
    
    const genres = movie.genres && movie.genres.length > 0
        ? movie.genres.slice(0, 3).map(g => `<span class="genre-tag">${g}</span>`).join('')
        : '';
    
    const platforms = movie.streaming_platforms && movie.streaming_platforms.length > 0
        ? movie.streaming_platforms.slice(0, 3).map(p => `<span class="platform-tag">${p}</span>`).join('')
        : '';

    return `
        <div class="movie-card" onclick="openLetterboxd('${movie.letterboxd_url || ''}')">
            <div class="movie-card-content">
                <div class="movie-title">${escapeHtml(movie.title)}</div>
                <div class="movie-year">${year}</div>
                
                <div class="movie-ratings">
                    <div class="rating">
                        <div class="rating-label">JustWatch</div>
                        <div class="rating-value">${jwRating}</div>
                    </div>
                    <div class="rating">
                        <div class="rating-label">Letterboxd</div>
                        <div class="rating-value">${lbRating}/5</div>
                    </div>
                </div>
                
                ${genres ? `<div class="movie-genres">${genres}</div>` : ''}
                ${platforms ? `<div class="movie-platforms">${platforms}</div>` : ''}
            </div>
        </div>
    `;
}

// Open Letterboxd page
function openLetterboxd(url) {
    if (url) {
        window.open(url, '_blank');
    }
}

// Show loading state
function showLoading() {
    const resultsSection = document.getElementById('resultsSection');
    const movieGrid = document.getElementById('movieGrid');
    
    resultsSection.classList.remove('hidden');
    movieGrid.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading movies...</p>
        </div>
    `;
}

// Show error message
function showError(message) {
    const resultsSection = document.getElementById('resultsSection');
    const movieGrid = document.getElementById('movieGrid');
    
    resultsSection.classList.remove('hidden');
    movieGrid.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${escapeHtml(message)}
        </div>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
