"""JustWatch API client wrapper

Provides a clean interface to the simple-justwatch-python-api library
with application-specific functionality and error handling.
"""

from typing import List, Optional
from simplejustwatchapi.justwatch import search, details
from simplejustwatchapi.query import MediaEntry


class JustWatchClient:
    """Client for interacting with JustWatch API"""
    
    def __init__(self, country: str = "US", language: str = "en"):
        """
        Initialize JustWatch client
        
        Args:
            country: ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "FR")
            language: ISO 639-1 language code (e.g., "en", "fr", "de")
        """
        self.country = country.upper()
        self.language = language.lower()
    
    def search_movies(
        self, 
        title: str, 
        count: int = 5, 
        best_only: bool = True
    ) -> List[MediaEntry]:
        """
        Search for movies by title
        
        Args:
            title: Movie title to search for
            count: Maximum number of results to return
            best_only: If True, only return best quality offers per platform
            
        Returns:
            List of MediaEntry objects matching the search
        """
        return search(
            title=title,
            country=self.country,
            language=self.language,
            count=count,
            best_only=best_only
        )
    
    def get_movie_details(self, entry_id: str, best_only: bool = True) -> MediaEntry:
        """
        Get detailed information for a specific movie
        
        Args:
            entry_id: JustWatch entry ID (e.g., "tm92641")
            best_only: If True, only return best quality offers per platform
            
        Returns:
            MediaEntry object with detailed movie information
        """
        return details(
            node_id=entry_id,
            country=self.country,
            language=self.language,
            best_only=best_only
        )
    
    def search_by_platform(
        self,
        title: str,
        platform: str,
        count: int = 10,
        best_only: bool = True
    ) -> List[MediaEntry]:
        """
        Search for movies available on a specific platform
        
        Args:
            title: Movie title to search for (empty string for all)
            platform: Platform name (e.g., "Netflix", "Hulu", "Amazon Prime")
            count: Maximum number of results
            best_only: If True, only return best quality offers
            
        Returns:
            List of movies available on the specified platform
        """
        results = self.search_movies(title, count=count, best_only=best_only)
        
        # Filter by platform
        filtered = []
        for movie in results:
            if movie.offers:
                # Check if any offer matches the platform
                for offer in movie.offers:
                    if platform.lower() in offer.package.name.lower():
                        filtered.append(movie)
                        break
        
        return filtered
    
    def get_streaming_platforms(self, movie: MediaEntry) -> List[str]:
        """
        Get list of streaming platforms where movie is available
        
        Args:
            movie: MediaEntry object
            
        Returns:
            List of platform names (e.g., ["Netflix", "Hulu"])
        """
        if not movie.offers:
            return []
        
        platforms = set()
        for offer in movie.offers:
            if offer.monetization_type == "FLATRATE":  # Subscription streaming
                platforms.add(offer.package.name)
        
        return sorted(list(platforms))
    
    def extract_imdb_id(self, movie: MediaEntry) -> Optional[str]:
        """
        Extract IMDb ID from movie entry
        
        Args:
            movie: MediaEntry object
            
        Returns:
            IMDb ID (e.g., "tt1375666") or None if not available
        """
        return movie.imdb_id if hasattr(movie, 'imdb_id') and movie.imdb_id else None
