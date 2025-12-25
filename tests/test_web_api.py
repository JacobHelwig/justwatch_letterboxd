#!/usr/bin/env python3
"""Test suite for FastAPI web application"""

import pytest
from fastapi.testclient import TestClient
from src.web.app import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_platforms():
    """Test platforms endpoint"""
    response = client.get("/api/platforms")
    assert response.status_code == 200
    platforms = response.json()
    assert isinstance(platforms, list)
    assert len(platforms) > 0
    assert "Netflix" in platforms


def test_search_movies():
    """Test search endpoint"""
    response = client.get("/api/search?query=Inception&count=5")
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data
    assert "total" in data
    assert isinstance(data["movies"], list)


def test_search_movies_invalid_count():
    """Test search with invalid count parameter"""
    response = client.get("/api/search?query=Inception&count=100")
    assert response.status_code == 422  # Validation error


def test_get_movies_by_platform():
    """Test get movies by platform endpoint"""
    response = client.get("/api/movies/Netflix?count=5")
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data
    assert "total" in data
    
    # Verify all movies have Netflix
    for movie in data["movies"]:
        assert "streaming_platforms" in movie
        if movie["streaming_platforms"]:
            assert any("Netflix" in platform for platform in movie["streaming_platforms"])


def test_get_movies_with_genre_filter():
    """Test platform movies with genre filter"""
    response = client.get("/api/movies/Netflix?count=10&genre=Action")
    assert response.status_code == 200
    data = response.json()
    
    # Verify genre filter applied
    for movie in data["movies"]:
        if movie["genres"]:
            assert "Action" in movie["genres"]


def test_get_movies_with_rating_filter():
    """Test platform movies with rating filter"""
    response = client.get("/api/movies/Netflix?count=10&min_rating=4.0")
    assert response.status_code == 200
    data = response.json()
    
    # Verify rating filter applied
    for movie in data["movies"]:
        if movie["letterboxd_rating"]:
            assert movie["letterboxd_rating"] >= 4.0
def test_get_movie_by_imdb_id():
    """Test get movie by IMDb ID - should require movie to be cached first"""
    # First, search for Inception to cache it
    search_response = client.get("/api/search?query=Inception&count=1")
    assert search_response.status_code == 200
    
    # Now try to get by IMDb ID (should be cached)
    response = client.get("/api/movie/tt1375666")
    assert response.status_code == 200
    movie = response.json()
    assert movie["imdb_id"] == "tt1375666"
    assert "title" in movie


def test_get_movie_not_found():
    """Test get movie with invalid IMDb ID"""
    response = client.get("/api/movie/tt0000000")
    assert response.status_code == 404


def test_cache_stats():
    """Test cache statistics endpoint"""
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_entries" in stats


def test_api_documentation():
    """Test that OpenAPI docs are available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test OpenAPI schema endpoint"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("Running FastAPI web application tests...\n")
    
    test_root_endpoint()
    print("✓ Root endpoint test passed")
    
    test_health_endpoint()
    print("✓ Health check test passed")
    
    if verbose:
        print("\nTest: get_platforms")
        response = client.get("/api/platforms")
        platforms = response.json()
        print(f"  Available platforms: {len(platforms)}")
        for platform in platforms[:3]:
            print(f"  - {platform}")
    
    test_get_platforms()
    print("✓ Get platforms test passed")
    
    if verbose:
        print("\nTest: search_movies")
        response = client.get("/api/search?query=Inception&count=3")
        data = response.json()
        print(f"  Found {data['total']} movies")
        for movie in data["movies"][:2]:
            print(f"  - {movie['title']} ({movie['year']}): {movie['letterboxd_rating']}/5.0")
    
    test_search_movies()
    print("✓ Search movies test passed")
    
    test_search_movies_invalid_count()
    print("✓ Search validation test passed")
    
    if verbose:
        print("\nTest: get_movies_by_platform")
        response = client.get("/api/movies/Netflix?count=3")
        data = response.json()
        print(f"  Found {data['total']} Netflix movies")
        for movie in data["movies"][:2]:
            print(f"  - {movie['title']}: {movie['letterboxd_rating'] or 'no rating'}")
    
    test_get_movies_by_platform()
    print("✓ Get movies by platform test passed")
    
    test_get_movies_with_genre_filter()
    print("✓ Genre filter test passed")
    
    test_get_movies_with_rating_filter()
    print("✓ Rating filter test passed")
    
    if verbose:
        print("\nTest: get_movie_by_imdb_id")
        response = client.get("/api/movie/tt1375666")
        movie = response.json()
        print(f"  Title: {movie['title']}")
        print(f"  IMDb ID: {movie['imdb_id']}")
        print(f"  Letterboxd rating: {movie['letterboxd_rating']}")
    
    test_get_movie_by_imdb_id()
    print("✓ Get movie by IMDb ID test passed")
    
    test_get_movie_not_found()
    print("✓ Movie not found test passed")
    
    test_cache_stats()
    print("✓ Cache stats test passed")
    
    test_api_documentation()
    print("✓ API documentation test passed")
    
    test_openapi_schema()
    print("✓ OpenAPI schema test passed")
    
    print("\n✓ All web API tests passed!")
    if not verbose:
        print("\nRun with --verbose or -v to see detailed output")
