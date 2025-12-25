#!/usr/bin/env python3
"""Test CatalogManager sync workflow with limited movies"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.catalog.manager import CatalogManager
from src.cache import MovieCache


async def test_catalog_manager():
    """Test catalog manager with a small sync"""
    print("Testing CatalogManager sync workflow")
    print("=" * 60)
    
    # Initialize with fresh cache for testing
    cache = MovieCache(cache_file=".cache/test_movies.db")
    manager = CatalogManager(cache=cache, log_dir="logs/test")
    
    print("\n1. Testing initial sync (first 3 pages)...")
    print("-" * 60)
    
    # Mock a small scrape for testing
    from src.scrapers.justwatch_netflix import NetflixScraper
    import httpx
    from bs4 import BeautifulSoup
    import re
    
    scraper = NetflixScraper()
    test_movies = []
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for page in range(1, 4):  # Only 3 pages for testing
            url = f"{scraper.base_url}?page={page}"
            print(f"Scraping page {page}...")
            
            response = await client.get(url, headers=scraper.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            movie_links = soup.find_all('a', href=re.compile(r'/movie/'))
            
            for link in movie_links:
                movie = scraper._extract_movie_data_from_link(link)
                if movie:
                    test_movies.append(movie)
            
            await asyncio.sleep(2)
    
    print(f"\nScraped {len(test_movies)} test movies")
    
    # Test catalog comparison (should be all new)
    print("\n2. Testing catalog comparison...")
    changes = await manager._compare_catalogs(test_movies)
    print(f"New: {len(changes['new'])}, Removed: {len(changes['removed'])}, Retained: {len(changes['retained'])}")
    
    # Test processing first 3 new titles (to test Letterboxd matching)
    print("\n3. Testing Letterboxd matching (first 3 movies only)...")
    sample_new = changes['new'][:3]
    matched, missing = await manager._process_new_titles(sample_new)
    print(f"Matched: {len(matched)}, Missing: {len(missing)}")
    
    if matched:
        print("\nMatched movies:")
        for movie in matched:
            print(f"  - {movie.title} ({movie.year}): Rating {movie.letterboxd_rating}")
    
    if missing:
        print("\nMissing from Letterboxd:")
        for movie in missing:
            print(f"  - {movie['title']} ({movie.get('year', 'N/A')})")
    
    # Test storing matched movies
    print("\n4. Testing cache storage...")
    await manager._store_matched_movies(matched)
    print(f"Stored {len(matched)} movies in cache")
    
    # Verify cache
    stats = cache.get_stats()
    print(f"Cache stats: {stats['total_entries']} entries")
    
    # Test get_platform_catalog
    print("\n5. Testing get_platform_catalog...")
    netflix_movies = cache.get_platform_catalog("Netflix")
    print(f"Found {len(netflix_movies)} Netflix movies in cache")
    
    print("\n" + "=" * 60)
    print("✅ CatalogManager test complete")
    
    return {
        'scraped': len(test_movies),
        'matched': len(matched),
        'missing': len(missing),
        'cached': stats['total_entries']
    }


if __name__ == "__main__":
    try:
        result = asyncio.run(test_catalog_manager())
        print(f"\nTest summary: {result}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
