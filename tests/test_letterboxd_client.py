#!/usr/bin/env python3
"""Test suite for Letterboxd client wrapper"""

import pytest
from src.letterboxd.client import LetterboxdClient


def test_client_initialization():
    """Test client initialization"""
    client = LetterboxdClient()
    assert client is not None


def test_get_movie():
    """Test fetching movie by slug"""
    client = LetterboxdClient()
    movie = client.get_movie("inception")
    
    assert movie is not None
    assert movie.title == "Inception"
    assert hasattr(movie, 'rating')


def test_get_movie_by_title():
    """Test fetching movie by title (converts to slug)"""
    client = LetterboxdClient()
    
    # Test with simple title
    movie = client.get_movie_by_title("Inception")
    assert movie is not None
    assert movie.title == "Inception"
    
    # Test with title requiring conversion
    movie2 = client.get_movie_by_title("The Matrix")
    assert movie2 is not None


def test_get_rating():
    """Test extracting rating from movie"""
    client = LetterboxdClient()
    movie = client.get_movie("inception")
    
    rating = client.get_rating(movie)
    assert rating is not None
    assert isinstance(rating, float)
    assert 0 <= rating <= 5.0


def test_get_genres():
    """Test extracting genres from movie"""
    client = LetterboxdClient()
    movie = client.get_movie("inception")
    
    genres = client.get_genres(movie)
    assert isinstance(genres, list)
    assert len(genres) > 0
    # Inception should have Action or Sci-Fi
    assert any(g in genres for g in ["Action", "Science Fiction", "Thriller"])


def test_extract_imdb_id():
    """Test extracting IMDb ID from movie"""
    client = LetterboxdClient()
    movie = client.get_movie("inception")
    
    imdb_id = client.extract_imdb_id(movie)
    assert imdb_id is not None
    assert imdb_id.startswith("tt")
    # Inception's IMDb ID
    assert imdb_id == "tt1375666"


def test_get_user():
    """Test fetching user profile"""
    client = LetterboxdClient()
    user = client.get_user("jack")
    
    assert user is not None
    assert user.username == "jack"
    assert hasattr(user, 'display_name')


def test_title_to_slug():
    """Test title to slug conversion"""
    client = LetterboxdClient()
    
    # Simple title
    assert client._title_to_slug("Inception") == "inception"
    
    # Title with spaces
    assert client._title_to_slug("The Matrix") == "the-matrix"
    
    # Title with special characters
    assert client._title_to_slug("Spider-Man: Homecoming") == "spider-man-homecoming"
    
    # Title with multiple spaces
    assert client._title_to_slug("The Lord  of the Rings") == "the-lord-of-the-rings"


def test_error_handling():
    """Test error handling for invalid movie"""
    client = LetterboxdClient()
    
    # Non-existent movie
    movie = client.get_movie("this-movie-definitely-does-not-exist-12345")
    assert movie is None


if __name__ == "__main__":
    print("Running Letterboxd client tests...\n")
    
    test_client_initialization()
    print("✓ Client initialization test passed")
    
    test_get_movie()
    print("✓ Get movie test passed")
    
    test_get_movie_by_title()
    print("✓ Get movie by title test passed")
    
    test_get_rating()
    print("✓ Get rating test passed")
    
    test_get_genres()
    print("✓ Get genres test passed")
    
    test_extract_imdb_id()
    print("✓ Extract IMDb ID test passed")
    
    test_get_user()
    print("✓ Get user test passed")
    
    test_title_to_slug()
    print("✓ Title to slug conversion test passed")
    
    test_error_handling()
    print("✓ Error handling test passed")
    
    print("\n✓ All tests passed!")
