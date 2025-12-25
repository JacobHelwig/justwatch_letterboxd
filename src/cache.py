"""Caching layer for movie data

Stores frequently accessed movie data in SQLite to reduce API calls
and improve performance.
"""

import sqlite3
import json
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from src.matcher import MatchedMovie


class MovieCache:
    """SQLite-based cache for movie data"""
    
    def __init__(self, cache_file: str = ".cache/movies.db"):
        """
        Initialize movie cache
        
        Args:
            cache_file: Path to SQLite database file
        """
        self.cache_file = cache_file
        self._ensure_cache_dir()
        self._init_db()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        cache_dir = Path(self.cache_file).parent
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imdb_id TEXT,
                    title TEXT NOT NULL,
                    year INTEGER,
                    justwatch_id TEXT,
                    streaming_platforms TEXT,
                    justwatch_rating REAL,
                    letterboxd_slug TEXT,
                    letterboxd_rating REAL,
                    genres TEXT,
                    letterboxd_url TEXT,
                    cached_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    UNIQUE(title, year)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_title ON movies(title)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_imdb_id ON movies(imdb_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cached_at ON movies(cached_at)
            """)
            conn.commit()
    
    def get(self, imdb_id: str, max_age_hours: int = 24) -> Optional[MatchedMovie]:
        """
        Get movie from cache
        
        Args:
            imdb_id: IMDb ID to look up
            max_age_hours: Maximum age of cached data in hours
            
        Returns:
            MatchedMovie object or None if not found or expired
        """
        with sqlite3.connect(self.cache_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM movies WHERE imdb_id = ?",
                (imdb_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Check if cache entry is expired
            cached_at = datetime.fromisoformat(row['cached_at'])
            if datetime.now() - cached_at > timedelta(hours=max_age_hours):
                return None
            
            # Update last accessed time
            conn.execute(
                "UPDATE movies SET last_accessed = ? WHERE imdb_id = ?",
                (datetime.now().isoformat(), imdb_id)
            )
            conn.commit()
            
            # Convert row to MatchedMovie
            return self._row_to_movie(row)
    
    def get_by_title(self, title: str, max_age_hours: int = 24) -> Optional[MatchedMovie]:
        """
        Get movie from cache by title
        
        Args:
            title: Movie title to search for
            max_age_hours: Maximum age of cached data in hours
            
        Returns:
            MatchedMovie object or None if not found or expired
        """
        with sqlite3.connect(self.cache_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM movies WHERE title LIKE ? ORDER BY cached_at DESC LIMIT 1",
                (f"%{title}%",)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Check if cache entry is expired
            cached_at = datetime.fromisoformat(row['cached_at'])
            if datetime.now() - cached_at > timedelta(hours=max_age_hours):
                return None
            
            return self._row_to_movie(row)
    
    def set(self, movie: MatchedMovie):
        """
        Store movie in cache
        
        Args:
            movie: MatchedMovie object to cache
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO movies (
                    imdb_id, title, year, justwatch_id, streaming_platforms,
                    justwatch_rating, letterboxd_slug, letterboxd_rating,
                    genres, letterboxd_url, cached_at, last_accessed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                movie.imdb_id,
                movie.title,
                movie.year,
                movie.justwatch_id,
                json.dumps(movie.streaming_platforms) if movie.streaming_platforms else None,
                movie.justwatch_rating,
                movie.letterboxd_slug,
                movie.letterboxd_rating,
                json.dumps(movie.genres) if movie.genres else None,
                movie.letterboxd_url,
                now,
                now
            ))
            conn.commit()
    
    def set_many(self, movies: List[MatchedMovie]):
        """
        Store multiple movies in cache
        
        Args:
            movies: List of MatchedMovie objects to cache
        """
        for movie in movies:
            self.set(movie)
    
    def clear_expired(self, max_age_hours: int = 168):
        """
        Remove expired cache entries
        
        Args:
            max_age_hours: Maximum age to keep (default: 1 week)
        """
        cutoff = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
        
        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.execute(
                "DELETE FROM movies WHERE cached_at < ?",
                (cutoff,)
            )
            deleted = cursor.rowcount
            conn.commit()
        
        return deleted
    
    def clear_all(self):
        """Clear all cache entries"""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("DELETE FROM movies")
            conn.commit()
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM movies")
            count = cursor.fetchone()[0]
            
            cursor = conn.execute(
                "SELECT MIN(cached_at) as oldest, MAX(cached_at) as newest FROM movies"
            )
            row = cursor.fetchone()
            
            return {
                "total_entries": count,
                "oldest_entry": row[0],
                "newest_entry": row[1]
            }
    
    def _row_to_movie(self, row: sqlite3.Row) -> MatchedMovie:
        """Convert database row to MatchedMovie object"""
        return MatchedMovie(
            title=row['title'],
            imdb_id=row['imdb_id'],
            year=row['year'],
            justwatch_id=row['justwatch_id'],
            streaming_platforms=json.loads(row['streaming_platforms']) if row['streaming_platforms'] else None,
            justwatch_rating=row['justwatch_rating'],
            letterboxd_slug=row['letterboxd_slug'],
            letterboxd_rating=row['letterboxd_rating'],
            genres=json.loads(row['genres']) if row['genres'] else None,
            letterboxd_url=row['letterboxd_url']
        )
    
    def get_platform_catalog(self, platform: str) -> List[dict]:
        """Get all movies for a specific streaming platform from cache
        
        Args:
            platform: Platform name (e.g., "Netflix")
        
        Returns:
            List of movie dicts with platform in streaming_platforms
        """
        with sqlite3.connect(self.cache_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM movies WHERE streaming_platforms LIKE ?",
                (f'%{platform}%',)
            )
            
            movies = []
            for row in cursor.fetchall():
                movie = self._row_to_movie(row)
                movies.append(movie.to_dict())
            
            return movies
    
    def delete(self, key: str):
        """Delete a cache entry by key
        
        Args:
            key: Cache key (e.g., "imdb:tt1234567" or "title:movie name")
        """
        # Parse key to determine lookup field
        if key.startswith("imdb:"):
            imdb_id = key.replace("imdb:", "")
            with sqlite3.connect(self.cache_file) as conn:
                conn.execute("DELETE FROM movies WHERE imdb_id = ?", (imdb_id,))
                conn.commit()
        elif key.startswith("title:"):
            title = key.replace("title:", "")
            with sqlite3.connect(self.cache_file) as conn:
                conn.execute("DELETE FROM movies WHERE LOWER(title) = ?", (title.lower(),))
                conn.commit()
