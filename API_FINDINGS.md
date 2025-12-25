# API Integration Test Results

**Date**: 2024-12-24  
**Goal**: Validate JustWatch and Letterboxd API access for Netflix movie discovery and rating lookup

## Summary

✅ **Both APIs successfully tested and validated**
- JustWatch: Can fetch Netflix movie availability
- Letterboxd: Can retrieve movie ratings and metadata
- No authentication required for either API
- Ready for production integration

---

## JustWatch API

### Library
- **Package**: `simple-justwatch-python-api` (v0.16)
- **Method**: Unofficial GraphQL API
- **Authentication**: None required
- **Installation**: `uv add simple-justwatch-python-api`

### Capabilities
- ✅ Search movies by title across regions
- ✅ Get detailed movie information by entry ID
- ✅ Filter by streaming platform (Netflix, Hulu, etc.)
- ✅ Query offers by country (US, GB, FR, etc.)
- ✅ Filter by quality (4K, HD, SD) with `best_only` parameter

### API Structure
```python
from simplejustwatchapi.justwatch import search, details

# Search for movies
results = search("Inception", country="US", language="en", count=5, best_only=True)

# MediaEntry attributes
movie = results[0]
movie.entry_id         # Unique identifier (e.g., "tm92641")
movie.title            # Movie title
movie.object_type      # "MOVIE" or "SHOW"
movie.year             # Release year
movie.rating           # Rating score
movie.genres           # List of genre dicts
movie.offers           # List of streaming offers
movie.imdb_id          # IMDb ID
movie.tmdb_id          # TMDB ID
movie.url              # JustWatch URL

# Offers structure
for offer in movie.offers:
    offer.package.name           # Platform name (e.g., "Netflix")
    offer.monetization_type      # "FLATRATE", "BUY", "RENT"
    offer.presentation_type      # "HD", "SD", "4K"
```

### Test Results
- **Inception**: Found, not on Netflix US
- **Stranger Things**: ✓ Found on Netflix
- **The Crown**: ✓ Found on Netflix
- **Squid Game**: ✓ Found on Netflix
- **Success Rate**: 3/3 Netflix titles verified

### Rate Limits
- No official rate limits documented
- Recommended: 1-2 second delay between requests
- Uses GraphQL (efficient, single request for multiple data points)

### Limitations
- ⚠️ Unofficial API - may break if JustWatch changes GraphQL schema
- ⚠️ Regional availability varies (must specify country)
- ⚠️ No official support or SLA

---

## Letterboxd API

### Library
- **Package**: `letterboxdpy` (v5.3.7)
- **Method**: Web scraping
- **Authentication**: None required for public data
- **Installation**: `uv add letterboxdpy`

### Capabilities
- ✅ Look up movies by slug (e.g., "inception")
- ✅ Retrieve ratings (1-5 scale)
- ✅ Get movie metadata (year, genres, directors)
- ✅ Access user profiles (public data only)
- ✅ Fetch reviews and lists

### API Structure
```python
from letterboxdpy.movie import Movie
from letterboxdpy.user import User

# Movie lookup
movie = Movie("inception")
movie.title            # Movie title
movie.year             # Release year
movie.rating           # Rating (e.g., 4.22)
movie.url              # Letterboxd URL
movie.genres           # List of genre dicts [{"name": "Action"}, ...]
movie.poster           # Poster image URL
movie.imdb_link        # IMDb link
movie.tmdb_link        # TMDB link

# User data
user = User("jack")
user.username          # Username
user.display_name      # Display name
```

### Test Results
- **Inception**: ✓ Rating 4.22/5.0
- **The Shawshank Redemption**: ✓ Rating 4.58/5.0
- **Pulp Fiction**: ✓ Rating 4.25/5.0
- **User Profile (jack)**: ✓ Successfully retrieved
- **Success Rate**: 3/3 movies + 1 user profile verified

### Rate Limits
- No official rate limits (web scraping)
- Recommended: 1-2 second delay to avoid blocking
- Excessive requests may result in IP-based throttling

### Limitations
- ⚠️ Web scraping - fragile to HTML changes
- ⚠️ No official API (requires approval for official access)
- ⚠️ Genres returned as dict objects (requires parsing)
- ⚠️ User data limited to public profiles
- ⚠️ Rating histogram counts not directly accessible

---

## Integration Strategy

### Matching Movies Between Services
**Recommended approach**: Use IMDb ID as primary key
- JustWatch provides: `movie.imdb_id`
- Letterboxd provides: `movie.imdb_link`
- Fallback: Match by title + year (less reliable due to internationalization)

### Workflow
1. **User input**: Select streaming service (e.g., Netflix)
2. **Fetch from JustWatch**: Get movies available on Netflix in user's region
3. **Enrich with Letterboxd**: Look up Letterboxd rating for each movie
4. **Display**: Show movies with availability + rating + genres
5. **Filter**: Allow sorting by rating, genre, year

### Performance Considerations
- **Batch processing**: Fetch multiple JustWatch results, then batch Letterboxd lookups
- **Caching**: Store results to reduce API calls (especially for popular titles)
- **Rate limiting**: 1-2 second delay between requests for each service
- **Parallel requests**: Use `asyncio` with `httpx` for concurrent API calls (within rate limits)

### Error Handling
- **JustWatch**: Handle empty results (movie not available in region)
- **Letterboxd**: Handle missing data (new movies may not have ratings yet)
- **Network errors**: Implement retry logic with exponential backoff
- **Parsing errors**: Gracefully handle schema changes in scraped data

---

## Configuration

### Environment Variables
See `.env.example` for configuration template:
```bash
JUSTWATCH_COUNTRY=US        # ISO 3166-1 alpha-2 code
JUSTWATCH_LANGUAGE=en       # ISO 639-1 code
LETTERBOXD_USERNAME=user    # Optional: default user
API_RATE_LIMIT_DELAY=1.0    # Seconds between requests
```

### No API Keys Required
- ✅ JustWatch: Unofficial GraphQL API (no auth)
- ✅ Letterboxd: Web scraping (no auth for public data)

---

## Next Steps

### Goal 1: ✅ COMPLETED
- [x] JustWatch API access validated
- [x] Letterboxd API access validated
- [x] Test scripts created and verified
- [x] API constraints documented
- [x] `.env.example` created

### Goal 2: Core Integration (Proposed)
- [ ] Create `src/` directory structure
- [ ] Implement JustWatch client wrapper
- [ ] Implement Letterboxd client wrapper
- [ ] Build movie matching logic (IMDb ID-based)
- [ ] Add caching layer (SQLite or JSON)
- [ ] Write integration tests

### Goal 3: CLI Interface (Proposed)
- [ ] Accept user input for streaming service selection
- [ ] Display movie results in formatted table
- [ ] Add filters (genre, rating threshold, year)
- [ ] Export results to CSV/JSON

---

## References

- **JustWatch API Library**: https://github.com/Electronic-Mango/simple-justwatch-python-api
- **Letterboxd API Library**: https://pypi.org/project/letterboxdpy/
- **JustWatch Website**: https://www.justwatch.com/
- **Letterboxd Website**: https://letterboxd.com/
