#!/usr/bin/env python3
"""Test suite for movie matching logic"""

import pytest
from src.matcher import MovieMatcher, MatchedMovie
from src.justwatch.client import JustWatchClient
from src.letterboxd.client import LetterboxdClient


def test_matcher_initialization():
    """Test matcher initialization"""
    matcher = MovieMatcher()
    assert matcher.justwatch is not None
    assert matcher.letterboxd is not None
    
    # Test with custom clients
    jw_client = JustWatchClient()
    lb_client = LetterboxdClient()
    matcher2 = MovieMatcher(jw_client, lb_client)
    assert matcher2.justwatch is jw_client
    assert matcher2.letterboxd is lb_client


def test_match_by_imdb_id():
    """Test matching movie using JustWatch data"""
    matcher = MovieMatcher()
    jw_client = JustWatchClient()
    
    # Search for Inception
    results = jw_client.search_movies("Inception", count=1)
    assert len(results) > 0
    
    # Match with Letterboxd
    matched = matcher.match_by_imdb_id(results[0])
    
    assert matched is not None
    assert matched.title == "Inception"
    assert matched.imdb_id is not None
    assert matched.imdb_id.startswith("tt")
    assert matched.letterboxd_rating is not None
    assert matched.letterboxd_rating > 0


def test_match_by_title():
    """Test matching movie by title"""
    matcher = MovieMatcher()
    
    matched = matcher.match_by_title("Inception")
    
    assert matched is not None
    assert "Inception" in matched.title
    assert matched.imdb_id is not None
    assert matched.letterboxd_rating is not None


def test_match_platform_movies():
    """Test matching movies from specific platform"""
    matcher = MovieMatcher()
    
    # Get Netflix movies (limit to 3 for speed)
    matched_movies = matcher.match_platform_movies("Netflix", count=3)
    
    assert len(matched_movies) > 0
    
    # Verify all have Netflix in streaming platforms
    for movie in matched_movies:
        assert movie.streaming_platforms is not None
        assert "Netflix" in movie.streaming_platforms
        assert movie.imdb_id is not None


def test_matched_movie_dataclass():
    """Test MatchedMovie dataclass"""
    movie = MatchedMovie(
        title="Test Movie",
        imdb_id="tt1234567",
        year=2020,
        streaming_platforms=["Netflix"],
        letterboxd_rating=4.2,
        genres=["Action", "Thriller"]
    )
    
    assert movie.title == "Test Movie"
    assert movie.imdb_id == "tt1234567"
    assert movie.year == 2020
    assert "Netflix" in movie.streaming_platforms
    assert movie.letterboxd_rating == 4.2
    assert "Action" in movie.genres


def test_partial_match():
    """Test creating partial match when Letterboxd data unavailable"""
    matcher = MovieMatcher()
    jw_client = JustWatchClient()
    
    # Search for movie that might not be on Letterboxd
    results = jw_client.search_movies("Stranger Things", count=1)
    
    if results:
        matched = matcher.match_by_imdb_id(results[0])
        
        # Should still create match with JustWatch data
        assert matched is not None
        assert matched.title is not None
        assert matched.imdb_id is not None
        assert matched.justwatch_id is not None


def test_match_with_genres():
    """Test that matched movies include genre data"""
    matcher = MovieMatcher()
    
    matched = matcher.match_by_title("Inception")
    
    assert matched is not None
    if matched.genres:  # Genres available if Letterboxd match succeeded
        assert isinstance(matched.genres, list)
        assert len(matched.genres) > 0


def test_match_with_streaming_platforms():
    """Test that matched movies include streaming platform data"""
    matcher = MovieMatcher()
    
    matched = matcher.match_by_title("Inception")
    
    assert matched is not None
    # Inception may or may not be on streaming platforms
    if matched.streaming_platforms:
        assert isinstance(matched.streaming_platforms, list)


if __name__ == "__main__":
    print("Running movie matcher tests...\n")
    
    test_matcher_initialization()
    print("✓ Matcher initialization test passed")
    
    test_match_by_imdb_id()
    print("✓ Match by IMDb ID test passed")
    
    test_match_by_title()
    print("✓ Match by title test passed")
    
    test_match_platform_movies()
    print("✓ Match platform movies test passed")
    
    test_matched_movie_dataclass()
    print("✓ MatchedMovie dataclass test passed")
    
    test_partial_match()
    print("✓ Partial match test passed")
    
    test_match_with_genres()
    print("✓ Match with genres test passed")
    
    test_match_with_streaming_platforms()
    print("✓ Match with streaming platforms test passed")
    
    print("\n✓ All tests passed!")
