#!/usr/bin/env python3
"""Test suite for movie cache"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from src.cache import MovieCache
from src.matcher import MatchedMovie


@pytest.fixture
def temp_cache():
    """Create temporary cache for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "test_cache.db")
        yield MovieCache(cache_file)


@pytest.fixture
def sample_movie():
    """Create sample movie for testing"""
    return MatchedMovie(
        title="Inception",
        imdb_id="tt1375666",
        year=2010,
        justwatch_id="tm92641",
        streaming_platforms=["Netflix", "Hulu"],
        justwatch_rating=8.1,
        letterboxd_slug="inception",
        letterboxd_rating=4.22,
        genres=["Action", "Sci-Fi", "Thriller"],
        letterboxd_url="https://letterboxd.com/film/inception/"
    )


def test_cache_initialization(temp_cache):
    """Test cache initialization"""
    assert temp_cache is not None
    assert os.path.exists(temp_cache.cache_file)


def test_set_and_get(temp_cache, sample_movie):
    """Test storing and retrieving movie from cache"""
    # Store movie
    temp_cache.set(sample_movie)
    
    # Retrieve movie
    cached = temp_cache.get(sample_movie.imdb_id)
    
    assert cached is not None
    assert cached.title == sample_movie.title
    assert cached.imdb_id == sample_movie.imdb_id
    assert cached.letterboxd_rating == sample_movie.letterboxd_rating
    assert cached.streaming_platforms == sample_movie.streaming_platforms


def test_get_by_title(temp_cache, sample_movie):
    """Test retrieving movie by title"""
    temp_cache.set(sample_movie)
    
    cached = temp_cache.get_by_title("Inception")
    
    assert cached is not None
    assert cached.imdb_id == sample_movie.imdb_id


def test_cache_expiration(temp_cache, sample_movie):
    """Test cache expiration"""
    temp_cache.set(sample_movie)
    
    # Should be in cache with default max_age
    cached = temp_cache.get(sample_movie.imdb_id, max_age_hours=24)
    assert cached is not None
    
    # Should be expired with very short max_age
    cached = temp_cache.get(sample_movie.imdb_id, max_age_hours=0)
    assert cached is None


def test_set_many(temp_cache):
    """Test storing multiple movies"""
    movies = [
        MatchedMovie(
            title="Movie 1",
            imdb_id="tt1111111",
            year=2020
        ),
        MatchedMovie(
            title="Movie 2",
            imdb_id="tt2222222",
            year=2021
        ),
        MatchedMovie(
            title="Movie 3",
            imdb_id="tt3333333",
            year=2022
        )
    ]
    
    temp_cache.set_many(movies)
    
    # Verify all stored
    for movie in movies:
        cached = temp_cache.get(movie.imdb_id)
        assert cached is not None
        assert cached.title == movie.title


def test_update_existing(temp_cache, sample_movie):
    """Test updating existing cache entry"""
    # Store initial version
    temp_cache.set(sample_movie)
    
    # Update movie data
    sample_movie.letterboxd_rating = 4.5
    temp_cache.set(sample_movie)
    
    # Verify updated
    cached = temp_cache.get(sample_movie.imdb_id)
    assert cached.letterboxd_rating == 4.5


def test_clear_expired(temp_cache, sample_movie):
    """Test clearing expired entries"""
    temp_cache.set(sample_movie)
    
    # Clear with very short max_age (should delete all)
    deleted = temp_cache.clear_expired(max_age_hours=0)
    assert deleted > 0
    
    # Verify cleared
    cached = temp_cache.get(sample_movie.imdb_id)
    assert cached is None


def test_clear_all(temp_cache, sample_movie):
    """Test clearing all cache entries"""
    temp_cache.set(sample_movie)
    
    temp_cache.clear_all()
    
    cached = temp_cache.get(sample_movie.imdb_id)
    assert cached is None


def test_get_stats(temp_cache, sample_movie):
    """Test cache statistics"""
    # Empty cache
    stats = temp_cache.get_stats()
    assert stats['total_entries'] == 0
    
    # Add movie
    temp_cache.set(sample_movie)
    
    stats = temp_cache.get_stats()
    assert stats['total_entries'] == 1
    assert stats['oldest_entry'] is not None
    assert stats['newest_entry'] is not None


def test_json_serialization(temp_cache, sample_movie):
    """Test JSON serialization of lists"""
    temp_cache.set(sample_movie)
    
    cached = temp_cache.get(sample_movie.imdb_id)
    
    # Verify lists are correctly serialized/deserialized
    assert isinstance(cached.streaming_platforms, list)
    assert isinstance(cached.genres, list)
    assert cached.streaming_platforms == sample_movie.streaming_platforms
    assert cached.genres == sample_movie.genres


def test_partial_data(temp_cache):
    """Test caching movie with partial data"""
    movie = MatchedMovie(
        title="Partial Movie",
        imdb_id="tt9999999",
        year=2023,
        streaming_platforms=None,
        genres=None
    )
    
    temp_cache.set(movie)
    cached = temp_cache.get(movie.imdb_id)
    
    assert cached is not None
    assert cached.title == movie.title
    assert cached.streaming_platforms is None
    assert cached.genres is None


if __name__ == "__main__":
    print("Running cache tests...\n")
if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("Running cache tests...\n")
    
    # Create temp cache for manual tests
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = os.path.join(tmpdir, "test_cache.db")
        cache = MovieCache(cache_file)
        
        sample = MatchedMovie(
            title="Inception",
            imdb_id="tt1375666",
            year=2010,
            streaming_platforms=["Netflix"],
            letterboxd_rating=4.22
        )
        
        if verbose:
            print("\nTest: cache operations")
            print(f"  Caching movie: {sample.title}")
        
        print("Testing cache operations...")
        cache.set(sample)
        cached = cache.get(sample.imdb_id)
        assert cached is not None
        
        if verbose:
            print(f"  Retrieved from cache: {cached.title}")
            print(f"  IMDb ID: {cached.imdb_id}")
            print(f"  Rating: {cached.letterboxd_rating}")
            print(f"  Platforms: {cached.streaming_platforms}")
        
        print("✓ Set and get test passed")
        
        stats = cache.get_stats()
        assert stats['total_entries'] == 1
        
        if verbose:
            print(f"\nCache stats:")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Oldest: {stats['oldest_entry']}")
            print(f"  Newest: {stats['newest_entry']}")
        
        print("✓ Stats test passed")
        
        cache.clear_all()
        cached = cache.get(sample.imdb_id)
        assert cached is None
        print("✓ Clear test passed")
    
    print("\n✓ All manual tests passed!")
    if not verbose:
        print("\nRun with --verbose or -v to see detailed output")
