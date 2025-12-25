#!/usr/bin/env python3
"""Test script for Letterboxd API - lookup movie ratings"""

from letterboxdpy.user import User
from letterboxdpy.movie import Movie

def test_letterboxd_movie_lookup():
    """Test Letterboxd movie lookup and rating retrieval"""
    print("=== Testing Letterboxd API ===\n")
    
    test_movies = [
        "inception",
        "the-shawshank-redemption",
        "pulp-fiction"
    ]
    
    print("1. Looking up movie ratings on Letterboxd...")
    successful_lookups = 0
    
    for movie_slug in test_movies:
        try:
            movie = Movie(movie_slug)
            print(f"\n   Movie: {movie.title}")
            print(f"   Year: {movie.year}")
            print(f"   Rating: {movie.rating}/5.0")
            # Rating count not directly available in letterboxdpy
            print(f"   URL: {movie.url}")
            
            if hasattr(movie, 'directors') and movie.directors:
                print(f"   Director(s): {', '.join(movie.directors)}")
            
            if hasattr(movie, 'genres') and movie.genres:
                genre_names = [g['name'] if isinstance(g, dict) else str(g) for g in movie.genres[:3]]
                print(f"   Genres: {', '.join(genre_names)}")
            
            successful_lookups += 1
            print(f"   ✓ Successfully retrieved data")
            
        except Exception as e:
            print(f"\n   ✗ Error looking up '{movie_slug}': {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✓ Successfully looked up {successful_lookups}/{len(test_movies)} movies")
    return successful_lookups > 0


def test_letterboxd_user_data():
    """Test Letterboxd user data retrieval (optional)"""
    print("\n2. Testing user data retrieval...")
    
    try:
        # Test with a public Letterboxd user
        user = User("jack")  # Letterboxd founder Jack Moulton
        print(f"   Username: {user.username}")
        print(f"   Display name: {user.display_name}")
        
        if hasattr(user, 'total_films_watched'):
            print(f"   Films watched: {user.total_films_watched}")
        
        print(f"   ✓ User data retrieval successful")
        return True
        
    except Exception as e:
        print(f"   - User data retrieval failed (might require authentication): {e}")
        return False


if __name__ == "__main__":
    print("Testing Letterboxd API integration\n")
    print("=" * 50)
    
    movie_success = test_letterboxd_movie_lookup()
    
    if movie_success:
        test_letterboxd_user_data()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    
    if movie_success:
        print("\n✓ Letterboxd API test successful!")
        print("  - Can retrieve movie ratings and metadata")
        print("  - Ready for integration with JustWatch data")
    else:
        print("\n✗ Letterboxd API test failed")
        print("  - Check letterboxdpy installation")
        print("  - Verify internet connectivity")
