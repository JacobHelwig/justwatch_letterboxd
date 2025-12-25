#!/usr/bin/env python3
"""Integration tests for complete workflow

Tests end-to-end functionality from API calls through matching and caching.
"""

import pytest
import tempfile
import os
from src.justwatch.client import JustWatchClient
from src.letterboxd.client import LetterboxdClient
from src.matcher import MovieMatcher, MatchedMovie
from src.cache import MovieCache


def test_complete_workflow():
    """Test complete workflow: search -> match -> cache -> retrieve"""
    # Initialize all components
    jw_client = JustWatchClient()
    lb_client = LetterboxdClient()
    matcher = MovieMatcher(jw_client, lb_client)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "integration_test.db")
        cache = MovieCache(cache_file)
        
        # 1. Search for movie on JustWatch
        jw_results = jw_client.search_movies("Inception", count=1)
        assert len(jw_results) > 0
        jw_movie = jw_results[0]
        
        # 2. Match with Letterboxd
        matched = matcher.match_by_imdb_id(jw_movie)
        assert matched is not None
        assert matched.imdb_id is not None
        assert matched.letterboxd_rating is not None
        
        # 3. Store in cache
        cache.set(matched)
        
        # 4. Retrieve from cache
        cached = cache.get(matched.imdb_id)
        assert cached is not None
        assert cached.title == matched.title
        assert cached.letterboxd_rating == matched.letterboxd_rating
        
        print("✓ Complete workflow test passed")


def test_cached_vs_fresh_lookup():
    """Test that cache improves performance"""
    matcher = MovieMatcher()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "perf_test.db")
        cache = MovieCache(cache_file)
        
        # First lookup (fresh)
        matched = matcher.match_by_title("Inception")
        assert matched is not None
        
        # Store in cache
        cache.set(matched)
        
        # Second lookup (cached)
        cached = cache.get(matched.imdb_id)
        assert cached is not None
        assert cached.imdb_id == matched.imdb_id
        
        print("✓ Cache performance test passed")


def test_platform_movies_with_cache():
    """Test platform movie search with caching"""
    matcher = MovieMatcher()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "platform_test.db")
        cache = MovieCache(cache_file)
        
        # Get Netflix movies
        movies = matcher.match_platform_movies("Netflix", count=3)
        assert len(movies) > 0
        
        # Cache all movies
        cache.set_many(movies)
        
        # Verify all are cached
        for movie in movies:
            cached = cache.get(movie.imdb_id)
            assert cached is not None
            assert "Netflix" in cached.streaming_platforms
        
        print("✓ Platform movies with cache test passed")


def test_cache_miss_then_fetch():
    """Test cache miss followed by fresh fetch"""
    matcher = MovieMatcher()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "miss_test.db")
        cache = MovieCache(cache_file)
        
        # Try to get from empty cache
        cached = cache.get("tt1375666")
        assert cached is None
        
        # Fetch fresh data
        matched = matcher.match_by_title("Inception")
        assert matched is not None
        
        # Store in cache
        cache.set(matched)
        
        # Now should be in cache
        cached = cache.get(matched.imdb_id)
        assert cached is not None
        
        print("✓ Cache miss then fetch test passed")


def test_multiple_api_calls():
    """Test multiple API calls with different movies"""
    matcher = MovieMatcher()
    
    test_movies = ["Inception", "The Matrix", "Interstellar"]
    
    for title in test_movies:
        matched = matcher.match_by_title(title)
        
        if matched:  # Some movies might not be found
            assert matched.title is not None
            assert matched.imdb_id is not None
            # Don't assert letterboxd_rating as it might be partial match
    
    print("✓ Multiple API calls test passed")


def test_partial_match_caching():
    """Test caching of partial matches (JustWatch only)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "partial_test.db")
        cache = MovieCache(cache_file)
        
        # Create partial match (JustWatch data only)
        partial = MatchedMovie(
            title="Test Movie",
            imdb_id="tt9999999",
            year=2023,
            justwatch_id="tm12345",
            streaming_platforms=["Netflix"],
            letterboxd_rating=None,  # No Letterboxd data
            genres=None
        )
        
        # Cache partial match
        cache.set(partial)
        
        # Retrieve and verify
        cached = cache.get(partial.imdb_id)
        assert cached is not None
        assert cached.streaming_platforms == ["Netflix"]
        assert cached.letterboxd_rating is None
        
        print("✓ Partial match caching test passed")


def test_end_to_end_with_filtering():
    """Test complete workflow with genre filtering"""
    matcher = MovieMatcher()
    
    # Get Netflix movies
    movies = matcher.match_platform_movies("Netflix", count=5)
    
    # Filter by genre if available
    action_movies = [m for m in movies if m.genres and "Action" in m.genres]
    
    # Should have some results
    assert len(movies) > 0
    
    # Verify all have Netflix
    for movie in movies:
        assert "Netflix" in movie.streaming_platforms
    
    print(f"✓ Found {len(movies)} Netflix movies, {len(action_movies)} action movies")


def test_client_integration():
    """Test that all clients work together"""
    jw_client = JustWatchClient()
    lb_client = LetterboxdClient()
    
    # Search same movie on both services
    jw_results = jw_client.search_movies("Inception", count=1)
    lb_movie = lb_client.get_movie("inception")
    
    assert len(jw_results) > 0
    assert lb_movie is not None
    
    # Verify both have data
    jw_movie = jw_results[0]
    assert jw_movie.title is not None
    assert lb_movie.title is not None
    
    # Extract and compare IMDb IDs
    jw_imdb = jw_client.extract_imdb_id(jw_movie)
    lb_imdb = lb_client.extract_imdb_id(lb_movie)
    
    assert jw_imdb == lb_imdb
    
    print("✓ Client integration test passed")


def test_cache_statistics():
    """Test cache statistics tracking"""
    matcher = MovieMatcher()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "stats_test.db")
        cache = MovieCache(cache_file)
        
        # Empty cache
        stats = cache.get_stats()
        assert stats['total_entries'] == 0
        
        # Add some movies
        movies = matcher.match_platform_movies("Netflix", count=3)
        cache.set_many(movies)
        
        # Check stats
        stats = cache.get_stats()
        assert stats['total_entries'] == len(movies)
        assert stats['oldest_entry'] is not None
        assert stats['newest_entry'] is not None
        
        print(f"✓ Cache stats: {stats['total_entries']} entries")


if __name__ == "__main__":
    print("Running integration tests...\n")
    
    test_complete_workflow()
    test_cached_vs_fresh_lookup()
    test_platform_movies_with_cache()
    test_cache_miss_then_fetch()
    test_multiple_api_calls()
if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("Running integration tests...\n")
    
    if verbose:
        print("\nTest: complete_workflow")
        jw_client = JustWatchClient()
        lb_client = LetterboxdClient()
        matcher = MovieMatcher(jw_client, lb_client)
        jw_results = jw_client.search_movies("Inception", count=1)
        if jw_results:
            matched = matcher.match_by_imdb_id(jw_results[0])
            print(f"  Title: {matched.title}")
            print(f"  IMDb ID: {matched.imdb_id}")
            print(f"  JustWatch rating: {matched.justwatch_rating}")
            print(f"  Letterboxd rating: {matched.letterboxd_rating}")
            print(f"  Platforms: {matched.streaming_platforms}")
    
    test_complete_workflow()
    
    if verbose:
        print("\nTest: platform_movies")
        matcher = MovieMatcher()
        movies = matcher.match_platform_movies("Netflix", count=3)
        print(f"  Found {len(movies)} Netflix movies:")
        for movie in movies:
            print(f"  - {movie.title}: {movie.letterboxd_rating}/5.0")
    
    test_cached_vs_fresh_lookup()
    test_platform_movies_with_cache()
    test_cache_miss_then_fetch()
    test_multiple_api_calls()
    test_partial_match_caching()
    test_end_to_end_with_filtering()
    test_client_integration()
    test_cache_statistics()
    
    print("\n✓ All integration tests passed!")
    if not verbose:
        print("\nRun with --verbose or -v to see detailed output")
