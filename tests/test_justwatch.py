#!/usr/bin/env python3
"""Test script for JustWatch API - fetch Netflix movies"""

from simplejustwatchapi.justwatch import search, details

def test_justwatch_search():
    """Test JustWatch search functionality for Netflix movies"""
    print("=== Testing JustWatch API ===\n")
    
    # Search for a popular movie
    print("1. Searching for 'Inception'...")
    try:
        results = search("Inception", country="US", language="en", count=5, best_only=True)
        print(f"   Found {len(results)} results")
        
        if results:
            first_result = results[0]
            print(f"   Title: {first_result.title}")
            print(f"   Entry ID: {first_result.entry_id}")
            print(f"   Object Type: {first_result.object_type}")
            print(f"   Object ID: {first_result.object_id}")
            
            # Check for Netflix offers
            if first_result.offers:
                netflix_offers = [offer for offer in first_result.offers 
                                 if 'netflix' in offer.package.name.lower()]
                if netflix_offers:
                    print(f"   ✓ Available on Netflix!")
                    for offer in netflix_offers:
                        print(f"     - {offer.package.name}: {offer.monetization_type}")
                else:
                    print(f"   ✗ Not available on Netflix in US")
            else:
                print(f"   No offers available")
            
            # Test details lookup
            print(f"\n2. Getting details for '{first_result.title}'...")
            detailed = details(first_result.entry_id, country="US", language="en", best_only=True)
            print(f"   Full title: {detailed.title}")
            if detailed.offers:
                print(f"   Total offers: {len(detailed.offers)}")
                platforms = set(offer.package.name for offer in detailed.offers)
                print(f"   Available on: {', '.join(platforms)}")
        
        print("\n✓ JustWatch API test successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ JustWatch API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_justwatch_netflix_movies():
    """Search for movies known to be on Netflix"""
    print("\n3. Searching for movies on Netflix...")
    
    test_titles = ["Stranger Things", "The Crown", "Squid Game"]
    netflix_found = 0
    
    for title in test_titles:
        try:
            results = search(title, country="US", language="en", count=3, best_only=True)
            if results and results[0].offers:
                netflix_offers = [offer for offer in results[0].offers 
                                 if 'netflix' in offer.package.name.lower()]
                if netflix_offers:
                    print(f"   ✓ '{title}' found on Netflix")
                    netflix_found += 1
                else:
                    print(f"   - '{title}' not on Netflix (found on other platforms)")
            else:
                print(f"   - '{title}' - no offers found")
        except Exception as e:
            print(f"   ✗ Error searching '{title}': {e}")
    
    print(f"\n   Found {netflix_found}/{len(test_titles)} titles on Netflix")
    return netflix_found > 0


if __name__ == "__main__":
    print("Testing JustWatch API integration\n")
    print("=" * 50)
    
    success = test_justwatch_search()
    if success:
        test_justwatch_netflix_movies()
    
    print("\n" + "=" * 50)
    print("Test complete!")
