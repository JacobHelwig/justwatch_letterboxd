#!/usr/bin/env python3
"""Inspect JustWatch Netflix page HTML structure

Fetches the page and analyzes HTML to determine correct selectors for scraping.
"""

import httpx
from bs4 import BeautifulSoup
import asyncio


async def inspect_page():
    """Fetch and inspect JustWatch Netflix page"""
    url = "https://www.justwatch.com/us/provider/netflix"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    print(f"Fetching: {url}\n")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for movie containers with various selectors
        print("=== Searching for movie containers ===\n")
        
        # Try different selectors
        selectors = [
            ('div.title-list-grid__item', 'Original selector'),
            ('div[class*="title"]', 'Divs with "title" in class'),
            ('a[href*="/movie/"]', 'Links to movie pages'),
            ('article', 'Article elements'),
            ('div[class*="grid"]', 'Divs with "grid" in class'),
        ]
        
        for selector, description in selectors:
            elements = soup.select(selector)
            print(f"{description} ({selector}): {len(elements)} found")
            if elements and len(elements) <= 5:
                print(f"  Sample classes: {elements[0].get('class')}")
        
        print("\n=== Analyzing first 3 movie links ===\n")
        
        # Find movie links
        movie_links = soup.find_all('a', href=lambda x: x and '/movie/' in x)[:3]
        
        for i, link in enumerate(movie_links, 1):
            print(f"Movie {i}:")
            print(f"  Title: {link.get('title', 'N/A')}")
            print(f"  Href: {link.get('href', 'N/A')}")
            print(f"  Text: {link.get_text(strip=True)[:50]}")
            
            # Check parent containers
            parent = link.parent
            for _ in range(3):  # Check 3 levels up
                if parent:
                    classes = parent.get('class', [])
                    if classes:
                        print(f"  Parent class: {' '.join(classes)}")
                    parent = parent.parent
            print()
        
        print("\n=== Looking for title containers ===\n")
        
        # Try to find the actual container structure
        movie_links = soup.find_all('a', href=lambda x: x and '/movie/' in x)[:1]
        if movie_links:
            link = movie_links[0]
            
            # Walk up the tree to find container
        print("\n=== Examining first tile structure ===\n")
        
        # Get first tile
        tiles = soup.find_all('div', class_='title-list-grid__item')
        if tiles:
            tile = tiles[0]
            print(f"Tile found: {tile.name}")
            print(f"Tile classes: {tile.get('class')}")
            
            # Look for links in tile
            links = tile.find_all('a', href=re.compile(r'/movie/'))
            print(f"Links in tile: {len(links)}")
            
            if links:
                link = links[0]
                print(f"  Link text: {link.get_text(strip=True)}")
                print(f"  Link href: {link.get('href')}")
            else:
                print("  No movie links found in tile!")
                print(f"  Tile HTML: {tile.prettify()[:500]}")


if __name__ == "__main__":
    import re
    asyncio.run(inspect_page())
