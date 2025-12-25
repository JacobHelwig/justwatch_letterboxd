#!/usr/bin/env python3
"""Test Netflix scraper pagination with limited page count"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.scrapers.justwatch_netflix import NetflixScraper


async def test_pagination():
    """Test scraper pagination for first 10 pages"""
    scraper = NetflixScraper()
    
    # Override max_pages for testing
    print("Testing Netflix scraper pagination (10 pages max)")
    print("=" * 60)
    
    movies = []
    page = 1
    max_pages = 10
    
    import httpx
    from bs4 import BeautifulSoup
    import re
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        while page <= max_pages:
            try:
                url = f"{scraper.base_url}?page={page}"
                print(f"\nScraping page {page}: {url}")
                
                response = await client.get(url, headers=scraper.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                movie_links = soup.find_all('a', href=re.compile(r'/movie/'))
                
                if not movie_links:
                    print(f"No movies found on page {page}, stopping")
                    break
                
                page_movies = []
                for link in movie_links:
                    movie = scraper._extract_movie_data_from_link(link)
                    if movie:
                        page_movies.append(movie)
                
                movies.extend(page_movies)
                print(f"Page {page}: Found {len(movie_links)} links, extracted {len(page_movies)} unique movies (total: {len(movies)})")
                
                page += 1
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
    
    print("\n" + "=" * 60)
    print(f"Test complete: {len(movies)} movies scraped from {page-1} pages")
    print(f"\nSample movies:")
    for movie in movies[:5]:
        print(f"  - {movie['title']} ({movie.get('year', 'N/A')})")
    
    return movies


if __name__ == "__main__":
    movies = asyncio.run(test_pagination())
    print(f"\n✅ Pagination test successful: {len(movies)} movies")
