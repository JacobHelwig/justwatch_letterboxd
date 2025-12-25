"""Catalog manager for Netflix movie synchronization and storage"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
from pathlib import Path

from ..cache import MovieCache
from ..scrapers.justwatch_netflix import NetflixScraper
from ..letterboxd.client import LetterboxdClient
from ..matcher import MovieMatcher, MatchedMovie

logger = logging.getLogger(__name__)


class CatalogManager:
    """Manages Netflix catalog syncing, change detection, and Letterboxd matching"""
    
    def __init__(
        self,
        cache: Optional[MovieCache] = None,
        scraper: Optional[NetflixScraper] = None,
        letterboxd_client: Optional[LetterboxdClient] = None,
        matcher: Optional[MovieMatcher] = None,
        log_dir: str = "logs"
    ):
        """Initialize catalog manager with dependencies
        
        Args:
            cache: MovieCache instance for storage
            scraper: NetflixScraper instance for web scraping
            letterboxd_client: LetterboxdClient for rating lookups
            matcher: MovieMatcher for matching movies
            log_dir: Directory for missing movies log
        """
        self.cache = cache or MovieCache()
        self.scraper = scraper or NetflixScraper()
        self.letterboxd_client = letterboxd_client or LetterboxdClient()
        self.matcher = matcher or MovieMatcher(
            letterboxd_client=self.letterboxd_client
        )
        
        # Set up logging for missing Letterboxd movies
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.missing_log = self.log_dir / "missing_letterboxd.log"
        
        # Set up file handler for missing movies
        self._setup_missing_logger()
    
    def _setup_missing_logger(self):
        """Configure logger for movies not found on Letterboxd"""
        missing_logger = logging.getLogger('catalog.missing')
        missing_logger.setLevel(logging.INFO)
        
        # Only add handler if not already present
        if not missing_logger.handlers:
            handler = logging.FileHandler(self.missing_log)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            missing_logger.addHandler(handler)
    
    async def sync_netflix_catalog(self) -> Dict[str, any]:
        """Run full Netflix catalog sync workflow
        
        Workflow:
        1. Scrape current Netflix catalog from JustWatch
        2. Compare with cached catalog to detect changes
        3. Query Letterboxd only for new titles
        4. Store matched movies in cache with 48h expiration
        5. Log movies not found on Letterboxd
        
        Returns:
            Dict with sync statistics: new, removed, retained, missing, total
        """
        logger.info("Starting Netflix catalog sync")
        start_time = datetime.now()
        
        # Step 1: Scrape current catalog
        logger.info("Scraping Netflix catalog from JustWatch...")
        current_titles = await self.scraper.scrape_catalog()
        logger.info(f"Scraped {len(current_titles)} titles from JustWatch")
        
        # Step 2: Load previous catalog and detect changes
        logger.info("Comparing with cached catalog...")
        changes = await self._compare_catalogs(current_titles)
        
        # Step 3: Process new titles (query Letterboxd)
        logger.info(f"Processing {len(changes['new'])} new titles...")
        matched, missing = await self._process_new_titles(changes['new'])
        
        # Step 4: Store matched movies in cache
        logger.info(f"Storing {len(matched)} matched movies in cache...")
        await self._store_matched_movies(matched)
        
        # Step 5: Log missing movies
        if missing:
            logger.info(f"Logging {len(missing)} missing Letterboxd titles...")
            self._log_missing_movies(missing)
        
        # Step 6: Clean up removed titles from cache
        if changes['removed']:
            logger.info(f"Removing {len(changes['removed'])} deleted titles from cache...")
            await self._remove_deleted_titles(changes['removed'])
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        stats = {
            'new': len(changes['new']),
            'removed': len(changes['removed']),
            'retained': len(changes['retained']),
            'matched': len(matched),
            'missing': len(missing),
            'total': len(current_titles),
            'elapsed_seconds': elapsed
        }
        
        logger.info(
            f"Sync complete: {stats['new']} new, {stats['removed']} removed, "
            f"{stats['retained']} retained, {stats['missing']} missing "
            f"({elapsed:.1f}s)"
        )
        
        return stats
    
    async def _compare_catalogs(self, current_titles: List[Dict]) -> Dict[str, List[Dict]]:
        """Compare current catalog with cached catalog to detect changes
        
        Args:
            current_titles: List of movie dicts from scraper
        
        Returns:
            Dict with 'new', 'removed', 'retained' lists
        """
        # Get cached Netflix titles
        cached_titles = self.cache.get_platform_catalog("Netflix")
        
        # Create sets for comparison (use title as key)
        current_set = {self._title_key(movie) for movie in current_titles}
        cached_set = {self._title_key(movie) for movie in cached_titles}
        
        # Detect changes
        new_keys = current_set - cached_set
        removed_keys = cached_set - current_set
        retained_keys = current_set & cached_set
        
        # Build title lists from keys
        new = [m for m in current_titles if self._title_key(m) in new_keys]
        removed = [m for m in cached_titles if self._title_key(m) in removed_keys]
        retained = [m for m in current_titles if self._title_key(m) in retained_keys]
        
        return {
            'new': new,
            'removed': removed,
            'retained': retained
        }
    
    def _title_key(self, movie: Dict) -> str:
        """Generate unique key for movie comparison
        
        Args:
            movie: Movie dict with title and optional year
        
        Returns:
            String key for comparison (title + year)
        """
        title = movie.get('title', '').strip().lower()
        year = movie.get('year', '')
        return f"{title}|{year}" if year else title
    
    async def _process_new_titles(self, new_titles: List[Dict]) -> tuple[List[MatchedMovie], List[Dict]]:
        """Query Letterboxd for new titles and match them
        
        Args:
            new_titles: List of new movie dicts from scraper
        
        Returns:
            Tuple of (matched_movies, missing_movies)
        """
        matched = []
        missing = []
        
        for movie in new_titles:
            try:
                # Try to match by title (IMDb ID not available from scraper)
                letterboxd_movie = self.letterboxd_client.get_movie_by_title(
                    movie['title']
                )
                
                if letterboxd_movie:
                    # Create MatchedMovie
                    matched_movie = MatchedMovie(
                        title=movie['title'],
                        year=movie.get('year'),
                        justwatch_id=movie.get('justwatch_id'),
                        imdb_id=letterboxd_movie.imdb_link.split('/')[-2] if letterboxd_movie.imdb_link else None,
                        letterboxd_rating=letterboxd_movie.rating,
                        letterboxd_url=letterboxd_movie.url,
                        genres=[g['name'] for g in letterboxd_movie.genres] if letterboxd_movie.genres else [],
                        streaming_platforms=['Netflix']
                    )
                    matched.append(matched_movie)
                else:
                    missing.append(movie)
                
                # Rate limiting - respect Letterboxd
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing {movie['title']}: {e}")
                missing.append(movie)
        
        return matched, missing
    
    async def _store_matched_movies(self, matched_movies: List[MatchedMovie]):
        """Store matched movies in cache with 48h expiration
        
        Args:
            matched_movies: List of MatchedMovie objects to store
        """
        for movie in matched_movies:
            self.cache.set(movie)

    
    def _log_missing_movies(self, missing_movies: List[Dict]):
        """Log movies not found on Letterboxd to file
        
        Args:
            missing_movies: List of movie dicts without Letterboxd matches
        """
        missing_logger = logging.getLogger('catalog.missing')
        
        for movie in missing_movies:
            missing_logger.info(
                f"Netflix: {movie['title']} ({movie.get('year', 'N/A')}) - "
                f"JustWatch ID: {movie.get('justwatch_id', 'N/A')}"
            )
    
    async def _remove_deleted_titles(self, removed_titles: List[Dict]):
        """Remove deleted titles from cache
        
        Args:
            removed_titles: List of movie dicts no longer on Netflix
        """
        for movie in removed_titles:
            # Remove by title
            title_key = f"title:{movie['title'].lower()}"
            self.cache.delete(title_key)
            
            # Remove by IMDb ID if available
            if movie.get('imdb_id'):
                imdb_key = f"imdb:{movie['imdb_id']}"
                self.cache.delete(imdb_key)
    
    def get_missing_movies(self) -> List[str]:
        """Get list of movies logged as missing from Letterboxd
        
        Returns:
            List of log lines for missing movies
        """
        if not self.missing_log.exists():
            return []
        
        with open(self.missing_log, 'r') as f:
            return f.readlines()
    
    def get_sync_status(self) -> Dict[str, any]:
        """Get current sync status and statistics
        
        Returns:
            Dict with cache stats and last sync info
        """
        stats = self.cache.get_stats()
        
        # Add missing movies count
        missing_count = len(self.get_missing_movies())
        
        return {
            'cache_stats': stats,
            'missing_movies': missing_count,
            'missing_log_path': str(self.missing_log)
        }
