#!/usr/bin/env python3
"""Test suite for JustWatch client wrapper"""

import pytest
from src.justwatch.client import JustWatchClient


def test_client_initialization():
    """Test client initialization with default and custom settings"""
    # Default settings
    client = JustWatchClient()
    assert client.country == "US"
    assert client.language == "en"
    
    # Custom settings
    client_uk = JustWatchClient(country="gb", language="en")
    assert client_uk.country == "GB"
    assert client_uk.language == "en"


def test_search_movies():
    """Test basic movie search functionality"""
    client = JustWatchClient()
    results = client.search_movies("Inception", count=3)
    
    assert len(results) > 0
    assert results[0].title == "Inception"
    assert hasattr(results[0], 'entry_id')


def test_get_movie_details():
    """Test fetching detailed movie information"""
    client = JustWatchClient()
    
    # First search for movie to get entry_id
    results = client.search_movies("Inception", count=1)
    assert len(results) > 0
    
    entry_id = results[0].entry_id
    details = client.get_movie_details(entry_id)
    
    assert details.title == "Inception"
    assert hasattr(details, 'entry_id')


def test_search_by_platform():
    """Test searching for movies on specific platform"""
    client = JustWatchClient()
    results = client.search_by_platform("Stranger Things", "Netflix", count=5)
    
    # Should find at least the main result
    assert len(results) > 0
    
    # Verify Netflix is in offers
    found_netflix = False
    for result in results:
        if result.offers:
            for offer in result.offers:
                if 'netflix' in offer.package.name.lower():
                    found_netflix = True
                    break
    
    assert found_netflix, "Netflix not found in search results"


def test_get_streaming_platforms():
    """Test extracting streaming platforms from movie"""
    client = JustWatchClient()
    results = client.search_movies("Stranger Things", count=1)
    
    assert len(results) > 0
    platforms = client.get_streaming_platforms(results[0])
    
    # Should return list of platform names
    assert isinstance(platforms, list)
    assert "Netflix" in platforms


def test_extract_imdb_id():
    """Test IMDb ID extraction"""
    client = JustWatchClient()
    results = client.search_movies("Inception", count=1)
    
    assert len(results) > 0
    imdb_id = client.extract_imdb_id(results[0])
    
    # Inception has IMDb ID
    assert imdb_id is not None
    assert imdb_id.startswith("tt")


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("Running JustWatch client tests...\n")
    
    test_client_initialization()
    print("✓ Client initialization test passed")
    
    if verbose:
        print("\nTest: search_movies")
        client = JustWatchClient()
        results = client.search_movies("Inception", count=3)
        print(f"  Found {len(results)} results")
        for i, movie in enumerate(results[:2]):
            print(f"  [{i+1}] {movie.title} ({movie.entry_id})")
    
    test_search_movies()
    print("✓ Search movies test passed")
    
    if verbose:
        print("\nTest: get_movie_details")
        client = JustWatchClient()
        results = client.search_movies("Inception", count=1)
        if results:
            details = client.get_movie_details(results[0].entry_id)
            print(f"  Title: {details.title}")
            print(f"  Entry ID: {details.entry_id}")
            if details.offers:
                print(f"  Offers: {len(details.offers)} platforms")
    
    test_get_movie_details()
    print("✓ Get movie details test passed")
    
    if verbose:
        print("\nTest: search_by_platform")
        client = JustWatchClient()
        results = client.search_by_platform("Stranger Things", "Netflix", count=3)
        print(f"  Found {len(results)} Netflix results")
        for movie in results[:2]:
            platforms = client.get_streaming_platforms(movie)
            print(f"  - {movie.title}: {platforms}")
    
    test_search_by_platform()
    print("✓ Search by platform test passed")
    
    if verbose:
        print("\nTest: get_streaming_platforms")
        client = JustWatchClient()
        results = client.search_movies("Stranger Things", count=1)
        if results:
            platforms = client.get_streaming_platforms(results[0])
            print(f"  {results[0].title} available on: {platforms}")
    
    test_get_streaming_platforms()
    print("✓ Get streaming platforms test passed")
    
    if verbose:
        print("\nTest: extract_imdb_id")
        client = JustWatchClient()
        results = client.search_movies("Inception", count=1)
        if results:
            imdb_id = client.extract_imdb_id(results[0])
            print(f"  {results[0].title} IMDb ID: {imdb_id}")
    
    test_extract_imdb_id()
    print("✓ Extract IMDb ID test passed")
    
    print("\n✓ All tests passed!")
    if not verbose:
        print("\nRun with --verbose or -v to see detailed output")
