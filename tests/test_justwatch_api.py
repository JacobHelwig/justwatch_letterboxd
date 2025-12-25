#!/usr/bin/env python3
"""Quick test to check JustWatch API for Netflix catalog size

Tests the simple-justwatch-python-api library to see how many Netflix titles
can be retrieved using different query approaches.
"""

from simplejustwatchapi.justwatch import search
import logging

logging.basicConfig(level=logging.INFO)

def test_search_approaches():
    """Test different search approaches to find Netflix movies"""
    
    print("\n=== Testing JustWatch API for Netflix Catalog ===\n")
    
    # Test 1: Empty search
    print("Test 1: Empty string search")
    try:
        results = search("", country="US", language="en", count=50)
        print(f"  Results: {len(results)} movies")
        if results:
            print(f"  Sample: {results[0].title}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 2: Common word search
    print("\nTest 2: Generic word 'the'")
    try:
        results = search("the", country="US", language="en", count=50)
        print(f"  Results: {len(results)} movies")
        if results:
            print(f"  Sample: {results[0].title}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 3: Check maximum count parameter
    print("\nTest 3: Maximum count (100)")
    try:
        results = search("", country="US", language="en", count=100)
        print(f"  Results: {len(results)} movies")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 4: Filter by provider using offers
    print("\nTest 4: Filter results by Netflix provider")
    try:
        all_results = search("", country="US", language="en", count=50)
        netflix_results = []
        for movie in all_results:
            if hasattr(movie, 'offers') and movie.offers:
                for offer in movie.offers:
                    if 'netflix' in offer.package.name.lower():
                        netflix_results.append(movie)
                        break
        print(f"  Total results: {len(all_results)}")
        print(f"  Netflix results: {len(netflix_results)}")
        if netflix_results:
            print(f"  Sample Netflix movie: {netflix_results[0].title}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 5: Multiple searches with different queries
    print("\nTest 5: Aggregate results from multiple searches")
    queries = ["the", "a", "love", "life", "night", "day", "man", "woman"]
    all_movies = {}
    try:
        for query in queries:
            results = search(query, country="US", language="en", count=50)
            for movie in results:
                if hasattr(movie, 'offers') and movie.offers:
                    for offer in movie.offers:
                        if 'netflix' in offer.package.name.lower():
                            if hasattr(movie, 'imdb_id') and movie.imdb_id:
                                all_movies[movie.imdb_id] = movie
                            break
        
        print(f"  Unique Netflix movies found: {len(all_movies)}")
        print(f"  Sample titles:")
        for i, movie in enumerate(list(all_movies.values())[:5]):
            print(f"    - {movie.title}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    test_search_approaches()
    print("\n=== Test Complete ===\n")
