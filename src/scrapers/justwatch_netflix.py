"""Netflix catalog scraper for JustWatch website

Scrapes all Netflix titles from https://www.justwatch.com/us/provider/netflix
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import time
import re

logger = logging.getLogger(__name__)


class NetflixScraper:
    """Scraper for JustWatch Netflix catalog"""
    
    def __init__(self, country: str = "us"):
        """
        Initialize Netflix scraper
        
        Args:
            country: Country code (default: "us")
        """
        self.country = country
        self.base_url = f"https://www.justwatch.com/{country}/provider/netflix"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    async def scrape_catalog(self) -> List[Dict]:
        """
        Scrape all Netflix titles from JustWatch
        
        Returns:
            List of movie dictionaries with title, year, imdb_id, justwatch_id
        """
        logger.info(f"Starting Netflix catalog scrape from {self.base_url}")
        start_time = time.time()
        
        movies = []
        page = 1
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            while True:
                try:
                    url = f"{self.base_url}?page={page}"
                    logger.info(f"Scraping page {page}: {url}")
                    
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Extract movie tiles - try multiple selectors
                    movie_tiles = soup.find_all('div', class_='title-list-grid__item')
                    
                    if not movie_tiles:
                        logger.info(f"No more movies found on page {page}, stopping")
                        break
                    
                    for tile in movie_tiles:
                        movie = self._extract_movie_data(tile)
                        if movie:
                            movies.append(movie)
                    
                    logger.info(f"Page {page}: Found {len(movie_tiles)} movies (total: {len(movies)})")
                    
                    # Check if there's a next page
                    next_page = soup.find('a', {'aria-label': 'Next Page'})
                    if not next_page:
                        logger.info("No next page link found, stopping")
                        break
                    
                    page += 1
                    
                    # Rate limiting - be respectful
                    import asyncio
                    await asyncio.sleep(2)
                    
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error on page {page}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error scraping page {page}: {e}")
                    break
        
        elapsed = time.time() - start_time
        logger.info(f"Scrape complete: {len(movies)} movies in {elapsed:.2f}s")
        
        return movies
    
    def _extract_movie_data(self, tile) -> Optional[Dict]:
        """
        Extract movie data from HTML tile
        
        Args:
            tile: BeautifulSoup element containing movie data
            
        Returns:
            Dictionary with movie data or None if extraction fails
        """
        try:
            # Extract title
            title_elem = tile.find('a', class_='title-list-grid__item--link')
            if not title_elem:
                return None
            
            title = title_elem.get('title', '').strip()
            href = title_elem.get('href', '')
            
            # Extract JustWatch ID from URL
            justwatch_id = None
            match = re.search(r'/movie/([^/]+)', href)
            if match:
                justwatch_id = match.group(1)
            
            # Extract year
            year_elem = tile.find('div', class_='title-list-grid__item--year')
            year = None
            if year_elem:
                year_text = year_elem.text.strip()
                year_match = re.search(r'\d{4}', year_text)
                if year_match:
                    year = int(year_match.group())
            
            # Extract IMDb ID from data attributes or links
            imdb_id = None
            imdb_link = tile.find('a', href=re.compile(r'imdb\.com/title/(tt\d+)'))
            if imdb_link:
                imdb_match = re.search(r'tt\d+', imdb_link.get('href', ''))
                if imdb_match:
                    imdb_id = imdb_match.group()
            
            if not title:
                return None
            
            return {
                'title': title,
                'year': year,
                'imdb_id': imdb_id,
                'justwatch_id': justwatch_id,
                'justwatch_url': f"https://www.justwatch.com{href}" if href else None
            }
            
        except Exception as e:
            logger.error(f"Error extracting movie data: {e}")
            return None
    
    async def get_movie_details(self, justwatch_id: str) -> Optional[Dict]:
        """
        Get detailed movie information from JustWatch
        
        Args:
            justwatch_id: JustWatch movie ID
            
        Returns:
            Dictionary with detailed movie data
        """
        url = f"https://www.justwatch.com/{self.country}/movie/{justwatch_id}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Extract IMDb ID from page
                imdb_link = soup.find('a', href=re.compile(r'imdb\.com/title/(tt\d+)'))
                imdb_id = None
                if imdb_link:
                    imdb_match = re.search(r'tt\d+', imdb_link.get('href', ''))
                    if imdb_match:
                        imdb_id = imdb_match.group()
                
                return {'imdb_id': imdb_id}
                
        except Exception as e:
            logger.error(f"Error fetching movie details for {justwatch_id}: {e}")
            return None


import asyncio

async def main():
    """Test scraper"""
    scraper = NetflixScraper()
    movies = await scraper.scrape_catalog()
    
    print(f"\nScraped {len(movies)} Netflix titles")
    print("\nSample movies:")
    for movie in movies[:5]:
        print(f"  - {movie['title']} ({movie['year']}) - IMDb: {movie['imdb_id']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
