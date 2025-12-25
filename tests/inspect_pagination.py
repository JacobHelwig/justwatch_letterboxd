#!/usr/bin/env python3
"""Inspect JustWatch pagination to understand why it stops after page 1"""

import httpx
from bs4 import BeautifulSoup
import asyncio
import re


async def inspect_pagination():
    """Check pagination structure on JustWatch Netflix page"""
    url = "https://www.justwatch.com/us/provider/netflix"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    print(f"Fetching: {url}\n")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        print("=== Searching for pagination elements ===\n")
        
        # Try different pagination selectors
        selectors = [
            ('a[aria-label="Next Page"]', 'Next Page link'),
            ('a[aria-label*="Next"]', 'Links with "Next"'),
            ('button[aria-label="Next Page"]', 'Next Page button'),
            ('a[href*="page="]', 'Links with page parameter'),
            ('nav[role="navigation"]', 'Navigation elements'),
            ('div[class*="pagination"]', 'Pagination divs'),
        ]
        
        for selector, description in selectors:
            elements = soup.select(selector)
            print(f"{description} ({selector}): {len(elements)} found")
            if elements:
                for elem in elements[:2]:
                    print(f"  Element: {elem.name}, class: {elem.get('class')}, href: {elem.get('href')}")
        
        print("\n=== Checking for lazy loading/JavaScript ===\n")
        
        # Check for data attributes that might indicate dynamic loading
        data_attrs = soup.find_all(attrs={"data-page": True})
        print(f"Elements with data-page: {len(data_attrs)}")
        
        # Check script tags for pagination config
        scripts = soup.find_all('script')
        print(f"Script tags: {len(scripts)}")
        for script in scripts[:3]:
            if script.string and ('page' in script.string.lower() or 'pagination' in script.string.lower()):
                print(f"  Script contains pagination-related code")
        
        print("\n=== Checking total movies available ===\n")
        
        # Look for total count indicators
        count_indicators = soup.find_all(text=re.compile(r'\d+\s*(titles|movies|results)'))
        print(f"Count indicators found: {len(count_indicators)}")
        for indicator in count_indicators[:3]:
            print(f"  - {indicator.strip()}")


if __name__ == "__main__":
    asyncio.run(inspect_pagination())
