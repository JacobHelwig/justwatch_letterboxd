"""Letterboxd API client wrapper

Provides a clean interface to the letterboxdpy library
with application-specific functionality and error handling.
"""

from typing import Optional
from letterboxdpy.movie import Movie
from letterboxdpy.user import User


class LetterboxdClient:
    """Client for interacting with Letterboxd API"""
    
    def __init__(self):
        """Initialize Letterboxd client"""
        pass
    
    def get_movie(self, slug: str) -> Optional[Movie]:
        """
        Get movie information by Letterboxd slug
        
        Args:
            slug: Letterboxd movie slug (e.g., "inception")
            
        Returns:
            Movie object or None if not found
        """
        try:
            return Movie(slug)
        except Exception as e:
            print(f"Error fetching movie '{slug}': {e}")
            return None
    
    def get_movie_by_title(self, title: str) -> Optional[Movie]:
        """
        Get movie by title (converts to slug format)
        
        Args:
            title: Movie title (e.g., "The Matrix")
            
        Returns:
            Movie object or None if not found
            
        Note:
            Converts title to slug format: "The Matrix" -> "the-matrix"
        """
        slug = self._title_to_slug(title)
        return self.get_movie(slug)
    
    def get_rating(self, movie: Movie) -> Optional[float]:
        """
        Extract rating from movie object
        
        Args:
            movie: Movie object
            
        Returns:
            Rating (0-5.0) or None if not available
        """
        if not movie:
            return None
        
        try:
            return movie.rating if hasattr(movie, 'rating') else None
        except Exception:
            return None
    
    def get_genres(self, movie: Movie) -> list[str]:
        """
        Extract genre names from movie object
        
        Args:
            movie: Movie object
            
        Returns:
            List of genre names (e.g., ["Action", "Sci-Fi"])
            
        Note:
            Letterboxd returns genres as dict objects with 'name' key
        """
        if not movie or not hasattr(movie, 'genres'):
            return []
        
        try:
            # Genres are dict objects: [{"name": "Action"}, ...]
            return [g['name'] if isinstance(g, dict) else str(g) for g in movie.genres]
        except Exception:
            return []
    
    def extract_imdb_id(self, movie: Movie) -> Optional[str]:
        """
        Extract IMDb ID from movie object
        
        Args:
            movie: Movie object
            
        Returns:
            IMDb ID (e.g., "tt1375666") or None if not available
            
        Note:
            Letterboxd provides imdb_link, need to parse ID from URL
        """
        if not movie or not hasattr(movie, 'imdb_link'):
            return None
        
        try:
            imdb_link = movie.imdb_link
            if imdb_link:
                # Extract ID from URL: http://www.imdb.com/title/tt1375666/maindetails
                # or https://www.imdb.com/title/tt1375666/
                if '/title/' in imdb_link:
                    # Find the IMDb ID pattern (tt followed by digits)
                    import re
                    match = re.search(r'(tt\d+)', imdb_link)
                    return match.group(1) if match else None
        except Exception:
            return None
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get user profile information
        
        Args:
            username: Letterboxd username
            
        Returns:
            User object or None if not found
        """
        try:
            return User(username)
        except Exception as e:
            print(f"Error fetching user '{username}': {e}")
            return None
    
    @staticmethod
    def _title_to_slug(title: str) -> str:
        """
        Convert movie title to Letterboxd slug format
        
        Args:
            title: Movie title (e.g., "The Matrix")
            
        Returns:
            Slug format (e.g., "the-matrix")
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower().strip()
        slug = slug.replace(' ', '-')
        
        # Remove special characters except hyphens
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # Remove duplicate hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        
        return slug.strip('-')
