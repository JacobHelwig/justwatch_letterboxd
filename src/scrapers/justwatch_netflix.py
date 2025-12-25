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
                    
                    # Extract movie links directly (tiles don't contain links)
                    movie_links = soup.find_all('a', href=re.compile(r'/movie/'))
                    
                    if not movie_links:
                        logger.info(f"No more movies found on page {page}, stopping")
                        break
                    
                    for link in movie_links:
                        movie = self._extract_movie_data_from_link(link)
                        if movie:
                            movies.append(movie)
                    
                    logger.info(f"Page {page}: Found {len(movie_links)} movies (total: {len(movies)})")
                    
                    # Continue to next page (no need to check for next page link)
                    # JustWatch uses sliding window pagination - just keep going until no movies found
                    page += 1
                    
                    # Rate limiting - be respectful (1 req/sec)
                    import asyncio
                    await asyncio.sleep(1)
                    
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error on page {page}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error scraping page {page}: {e}")
                    break
        
        elapsed = time.time() - start_time
        logger.info(f"Scrape complete: {len(movies)} movies in {elapsed:.2f}s")
        
        return movies
    
    def _extract_movie_data_from_link(self, link) -> Optional[Dict]:
        """
        Extract movie data from movie link element
        
        Args:
            link: BeautifulSoup anchor element with movie link
            
        Returns:
            Dictionary with movie data or None if extraction fails
        """
        try:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            
            if not title or not href:
                return None
            
            logger.debug(f"Found movie: {title}, href: {href}")
            
            # Extract JustWatch ID from URL
            justwatch_id = None
            match = re.search(r'/movie/([^/?]+)', href)
            if match:
                justwatch_id = match.group(1)
            
            # Extract year - look in surrounding text
            parent = link.parent
            year = None
            if parent:
                parent_text = parent.get_text()
                year_match = re.search(r'\b(19|20)\d{2}\b', parent_text)
                if year_match:
                    year = int(year_match.group())
            
            # IMDb ID not available in list view
            imdb_id = None
            
            logger.debug(f"Extracted: {title} ({year}) - {justwatch_id}")
            
            return {
                'title': title,
                'year': year,
                'imdb_id': imdb_id,
                'justwatch_id': justwatch_id,
                'justwatch_url': f"https://www.justwatch.com{href}" if href.startswith('/') else href
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
