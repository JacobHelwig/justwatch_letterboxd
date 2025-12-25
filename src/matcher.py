"""Movie matching logic for JustWatch and Letterboxd integration

Matches movies between JustWatch streaming availability and Letterboxd ratings
using IMDb IDs as the primary key.
"""

from typing import Optional, List
from dataclasses import dataclass
from src.justwatch.client import JustWatchClient
from src.letterboxd.client import LetterboxdClient
from simplejustwatchapi.query import MediaEntry
from letterboxdpy.movie import Movie


@dataclass
class MatchedMovie:
    """Matched movie data from JustWatch and Letterboxd"""
    
    # Common fields
    title: str
    imdb_id: str
    year: Optional[int] = None
    
    # JustWatch data
    justwatch_id: Optional[str] = None
    streaming_platforms: Optional[List[str]] = None
    justwatch_rating: Optional[float] = None
    
    # Letterboxd data
    letterboxd_slug: Optional[str] = None
    letterboxd_rating: Optional[float] = None
    genres: Optional[List[str]] = None
    letterboxd_url: Optional[str] = None


class MovieMatcher:
    """Matches movies between JustWatch and Letterboxd"""
    
    def __init__(
        self, 
        justwatch_client: Optional[JustWatchClient] = None,
        letterboxd_client: Optional[LetterboxdClient] = None
    ):
        """
        Initialize movie matcher
        
        Args:
            justwatch_client: JustWatch client instance (creates default if None)
            letterboxd_client: Letterboxd client instance (creates default if None)
        """
        self.justwatch = justwatch_client or JustWatchClient()
        self.letterboxd = letterboxd_client or LetterboxdClient()
    
    def match_by_imdb_id(
        self, 
        justwatch_movie: MediaEntry,
        letterboxd_slug: Optional[str] = None
    ) -> Optional[MatchedMovie]:
        """
        Match a JustWatch movie with Letterboxd data using IMDb ID
        
        Args:
            justwatch_movie: JustWatch MediaEntry object
            letterboxd_slug: Optional Letterboxd slug if already known
            
        Returns:
            MatchedMovie object or None if no match found
        """
        # Extract IMDb ID from JustWatch
        imdb_id = self.justwatch.extract_imdb_id(justwatch_movie)
        if not imdb_id:
            return None
        
        # Get Letterboxd movie
        if letterboxd_slug:
            letterboxd_movie = self.letterboxd.get_movie(letterboxd_slug)
        else:
            # Try to find by title (fallback method)
            letterboxd_movie = self.letterboxd.get_movie_by_title(justwatch_movie.title)
        
        # Verify IMDb ID match if Letterboxd movie found
        if letterboxd_movie:
            letterboxd_imdb_id = self.letterboxd.extract_imdb_id(letterboxd_movie)
            if letterboxd_imdb_id != imdb_id:
                # IMDb IDs don't match, try fallback
                return self._create_partial_match(justwatch_movie, imdb_id)
        else:
            return self._create_partial_match(justwatch_movie, imdb_id)
        
        # Create matched movie object
        return self._create_matched_movie(justwatch_movie, letterboxd_movie, imdb_id)
    
    def match_by_title(self, title: str) -> Optional[MatchedMovie]:
        """
        Match a movie by title across both services
        
        Args:
            title: Movie title to search for
            
        Returns:
            MatchedMovie object or None if no match found
        """
        # Search JustWatch first
        justwatch_results = self.justwatch.search_movies(title, count=1)
        if not justwatch_results:
            return None
        
        justwatch_movie = justwatch_results[0]
        return self.match_by_imdb_id(justwatch_movie)
    
    def match_platform_movies(
        self,
        platform: str,
        count: int = 10
    ) -> List[MatchedMovie]:
        """
        Get matched movies for a specific streaming platform
        
        Args:
            platform: Platform name (e.g., "Netflix", "Hulu")
            count: Maximum number of movies to match
            
        Returns:
            List of MatchedMovie objects
        """
        # Search JustWatch for platform movies
        # Using empty string for title to get popular movies on platform
        justwatch_movies = self.justwatch.search_by_platform("", platform, count=count)
        
        matched_movies = []
        for jw_movie in justwatch_movies:
            matched = self.match_by_imdb_id(jw_movie)
            if matched:
                matched_movies.append(matched)
        
        return matched_movies
    
    def _create_matched_movie(
        self,
        justwatch_movie: MediaEntry,
        letterboxd_movie: Movie,
        imdb_id: str
    ) -> MatchedMovie:
        """Create MatchedMovie from both data sources"""
        return MatchedMovie(
            title=justwatch_movie.title,
            imdb_id=imdb_id,
            year=getattr(justwatch_movie, 'year', None),
            justwatch_id=justwatch_movie.entry_id,
            streaming_platforms=self.justwatch.get_streaming_platforms(justwatch_movie),
            justwatch_rating=getattr(justwatch_movie, 'rating', None),
            letterboxd_slug=letterboxd_movie.url.split('/')[-2] if letterboxd_movie.url else None,
            letterboxd_rating=self.letterboxd.get_rating(letterboxd_movie),
            genres=self.letterboxd.get_genres(letterboxd_movie),
            letterboxd_url=letterboxd_movie.url
        )
    
    def _create_partial_match(
        self,
        justwatch_movie: MediaEntry,
        imdb_id: str
    ) -> MatchedMovie:
        """Create MatchedMovie with only JustWatch data"""
        return MatchedMovie(
            title=justwatch_movie.title,
            imdb_id=imdb_id,
            year=getattr(justwatch_movie, 'year', None),
            justwatch_id=justwatch_movie.entry_id,
            streaming_platforms=self.justwatch.get_streaming_platforms(justwatch_movie),
            justwatch_rating=getattr(justwatch_movie, 'rating', None)
        )
