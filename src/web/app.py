"""FastAPI web application for JustWatch + Letterboxd integration"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import time
import logging

from src.justwatch.client import JustWatchClient
from src.letterboxd.client import LetterboxdClient
from src.matcher import MovieMatcher, MatchedMovie
from src.cache import MovieCache

# Configure logging for profiling
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API responses
class MovieResponse(BaseModel):
    """Movie response model"""
    title: str
    imdb_id: str
    year: Optional[int] = None
    justwatch_id: Optional[str] = None
    streaming_platforms: Optional[List[str]] = None
    justwatch_rating: Optional[float] = None
    letterboxd_slug: Optional[str] = None
    letterboxd_rating: Optional[float] = None
    genres: Optional[List[str]] = None
    letterboxd_url: Optional[str] = None


class PlatformResponse(BaseModel):
    """Streaming platform response model"""
    name: str
    count: int


class SearchResponse(BaseModel):
    """Search results response model"""
    movies: List[MovieResponse]
    total: int


# Initialize FastAPI app
app = FastAPI(
    title="JustWatch + Letterboxd Integration",
    description="Web API for discovering movies with streaming availability and ratings",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
jw_client = JustWatchClient()
lb_client = LetterboxdClient()
matcher = MovieMatcher(jw_client, lb_client)
cache = MovieCache()
# Initialize clients
jw_client = JustWatchClient()
lb_client = LetterboxdClient()
matcher = MovieMatcher(jw_client, lb_client)
cache = MovieCache()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main HTML page"""
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text())


# Mount static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/platforms", response_model=List[str])
async def get_platforms():
    """
    Get list of available streaming platforms
    
    Returns:
        List of platform names
    """
    # Common streaming platforms
    platforms = [
        "Netflix",
        "Amazon Prime Video",
        "Hulu",
        "Disney Plus",
        "HBO Max",
        "Apple TV Plus",
        "Paramount Plus",
        "Peacock"
    ]
    return platforms


@app.get("/api/search", response_model=SearchResponse)
async def search_movies(
    query: str = Query(..., description="Movie title to search for"),
    count: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """
    Search for movies by title
    
    Args:
        query: Movie title to search for
        count: Number of results to return (1-50)
    
    Returns:
        SearchResponse with matched movies
    """
    try:
        # Search on JustWatch
        jw_results = jw_client.search_movies(query, count=count)
        
        # Match with Letterboxd and cache results
        movies = []
        for jw_movie in jw_results:
            matched = matcher.match_by_imdb_id(jw_movie)
        return SearchResponse(movies=movies, total=len(movies))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
@app.get("/api/movies/{platform}", response_model=SearchResponse)
async def get_movies_by_platform(
    platform: str,
    count: int = Query(20, ge=1, le=50, description="Number of results to return"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum Letterboxd rating"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Maximum Letterboxd rating"),
    year: Optional[int] = Query(None, ge=1900, le=2100, description="Filter by release year")
):
    """
    Get movies available on a specific streaming platform
    
    Args:
        platform: Streaming platform name
        count: Number of results to return (1-50)
        genre: Filter by genre
        min_rating: Minimum Letterboxd rating (0-5)
        max_rating: Maximum Letterboxd rating (0-5)
        year: Filter by release year
    
    Returns:
        SearchResponse with matched movies sorted by Letterboxd rating
    """
    start_time = time.time()
    
    try:
        # Get movies from platform
        logger.info(f"Fetching {count} movies from {platform}")
        fetch_start = time.time()
        movies = matcher.match_platform_movies(platform, count=count)
        fetch_time = time.time() - fetch_start
        logger.info(f"Fetched {len(movies)} movies in {fetch_time:.2f}s ({fetch_time/len(movies) if movies else 0:.2f}s per movie)")
        
        # Apply filters
        filter_start = time.time()
        filtered_movies = []
        for movie in movies:
            # Genre filter
            if genre and (not movie.genres or genre not in movie.genres):
                continue
            
            # Rating filters
            if min_rating is not None and (not movie.letterboxd_rating or movie.letterboxd_rating < min_rating):
                continue
            if max_rating is not None and (not movie.letterboxd_rating or movie.letterboxd_rating > max_rating):
                continue
            
            # Year filter
            if year and movie.year != year:
                continue
            
            filtered_movies.append(MovieResponse(**movie.__dict__))
        
        filter_time = time.time() - filter_start
        logger.info(f"Filtered to {len(filtered_movies)} movies in {filter_time:.2f}s")
        
        # Sort by Letterboxd rating (highest first), movies without rating go to end
        sort_start = time.time()
        filtered_movies.sort(
            key=lambda m: (m.letterboxd_rating is not None, m.letterboxd_rating or 0),
            reverse=True
        )
        sort_time = time.time() - sort_start
        logger.info(f"Sorted movies in {sort_time:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total request time: {total_time:.2f}s")
        
        return SearchResponse(movies=filtered_movies, total=len(filtered_movies))
    except Exception as e:
        logger.error(f"Error fetching platform movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
        return SearchResponse(movies=filtered_movies, total=len(filtered_movies))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movie/{imdb_id}", response_model=MovieResponse)
async def get_movie(imdb_id: str):
    """
    Get movie details by IMDb ID
    
    Args:
        imdb_id: IMDb ID (e.g., tt1375666)
    
    Returns:
        MovieResponse with movie details
    """
    try:
        # Check cache first
        cached = cache.get(imdb_id)
        if cached:
            return MovieResponse(**cached.__dict__)
        
        # If not in cache, need to search by title or fetch from APIs
        # Since we can't search JustWatch directly by IMDb ID,
        # we'll return 404 and recommend using search endpoint first
        raise HTTPException(
            status_code=404, 
            detail="Movie not found in cache. Use /api/search to find movies first."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics
    
    Returns:
        Cache statistics
    """
    try:
        stats = cache.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
