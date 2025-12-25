# AGENTS.md

This file provides guidance to agents (i.e., ADAL) when working with code in this repository.

## Project Overview

**justwatch_letterboxd** - A web application that integrates JustWatch streaming availability data with Letterboxd movie ratings.

**Current Status**: Goal 1 completed - API integration validated

## Project Intent

JustWatch is a popular service that aggregates streaming availability for movies and TV shows across various platforms such as Netflix and Hulu. Letterboxd is a social platform for film enthusiasts to track and review movies. This project aims to allow users to look at Letterboxd scores for movies that are available on their streaming platform of choice via JustWatch.

The base user workflow would be:
1. User selects their streaming services.
2. Our tool fetches movies available on this service from JustWatch and includes Letterboxd ratings for those movies.
3. The user can filter based on information from JustWatch and Letterboxd.


## Development Setup 

- **Language/Framework**: Python 3.14+
- **Package Manager**: uv
- **Dependencies**: simple-justwatch-python-api, letterboxdpy, httpx, pytest
- **API Keys Required**: None (both APIs use unofficial methods)
- **Environment Variables**: See `.env.example`

## Essential Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run python tests/test_justwatch.py
uv run python tests/test_letterboxd.py

# Run all tests with pytest
uv run pytest

# Run linter
uv run ruff check .

# Format code
uv run ruff format .
```

## Development Workflow
## Development Workflow

**Branch-Based Development**:
- Always develop on feature branches (e.g., `adal/goal-2-core-integration`)
- Never commit directly to main
- Open PR for review before merging to main
- Delete branch after merging

**Incremental Development**:
- Commit changes incrementally after each logical unit of work
- Run tests after each implementation before committing
- Never commit broken code or failing tests

**Documentation Maintenance**:
- Update `README.md` after completing features or milestones
**Pre-Commit Checklist**:
1. ✅ Tests pass (`uv run pytest`)
2. ✅ Linter clean (`uv run ruff check .`)
3. ✅ Docs updated (README.md, AGENTS.md reflect changes)
4. ✅ Commit message descriptive with co-authorship

**Git Commit Co-Authorship**:
All commits made by AdaL should include co-authorship line at the end of commit message:
```
Co-Authored-By: AdaL <adal@sylph.ai>
```

**Testing Requirements**:
- All new features must include tests when feasible
- Tests should cover core functionality and edge cases
- Run tests before committing to ensure they pass
- Test files should be named `test_*.py` and placed in `tests/` directory
## API Integration Details

### JustWatch API
- **Library**: `simple-justwatch-python-api` (v0.16)
- **Method**: Unofficial GraphQL API
- **Authentication**: None required
- **Rate Limits**: No official limits, recommend 1-2 second delays

**Key Attributes**:
```python
from simplejustwatchapi.justwatch import search, details

movie = search("title", country="US", language="en")[0]
movie.entry_id         # Unique ID (e.g., "tm92641")
movie.title            # Movie title
movie.offers           # List of streaming offers
movie.imdb_id          # IMDb ID (for matching)
movie.tmdb_id          # TMDB ID
movie.genres           # Genre dicts

# Offers
offer.package.name           # "Netflix", "Hulu", etc.
offer.monetization_type      # "FLATRATE", "BUY", "RENT"
offer.presentation_type      # "HD", "SD", "4K"
```

**Gotchas**:
- ⚠️ Unofficial API - may break if schema changes
- ⚠️ Must specify country/language for correct regional availability
- ⚠️ `entry_id` not `node_id` (common mistake)

### Letterboxd API
- **Library**: `letterboxdpy` (v5.3.7)
- **Method**: Web scraping
- **Authentication**: None for public data
- **Rate Limits**: No official limits, recommend 1-2 second delays

**Key Attributes**:
```python
from letterboxdpy.movie import Movie
from letterboxdpy.user import User

movie = Movie("inception")  # Use slug, not title
movie.title            # Movie title
movie.rating           # Rating (e.g., 4.22/5.0)
movie.year             # Release year
movie.genres           # List of DICTS: [{"name": "Action"}, ...]
movie.imdb_link        # IMDb link (for matching)
movie.url              # Letterboxd URL
```

**Gotchas**:
- ⚠️ Web scraping - fragile to HTML changes
- ⚠️ Genres are dict objects with 'name' key (not strings)
- ⚠️ Must use slug format: "the-matrix" not "The Matrix"
- ⚠️ New movies may not have ratings yet

### API Test Results

**JustWatch API** (`simple-justwatch-python-api` v0.16):
- **Test Cases**: Inception (not on Netflix US), Stranger Things ✅, The Crown ✅, Squid Game ✅
- **Success Rate**: 3/3 Netflix titles verified
- **Performance**: ~1-2 seconds per query via GraphQL
- **Observations**: Regional availability differs significantly; IMDb/TMDB IDs provided for cross-referencing

**Letterboxd API** (`letterboxdpy` v5.3.7):
- **Test Cases**: Inception (4.22/5.0) ✅, Shawshank Redemption (4.58/5.0) ✅, Pulp Fiction (4.25/5.0) ✅, User profile (jack) ✅
- **Success Rate**: 3/3 movies + 1 user profile verified
- **Performance**: 2-4 seconds per movie via web scraping
- **Observations**: Genres returned as dict objects with 'name' key; IMDb links available for cross-referencing

### Integration Strategy
**Movie Matching**:
- **Primary**: Use IMDb ID (both APIs provide)
  - JustWatch: `movie.imdb_id`
  - Letterboxd: `movie.imdb_link` (extract ID from URL)
- **Fallback**: Title + year matching (less reliable)

**Workflow**:
1. Fetch movies from JustWatch for selected platform/region
2. Extract IMDb IDs from results
3. Look up Letterboxd data using IMDb IDs
4. Merge and display combined data

**Performance**:
- Rate limiting: 1-2 second delays between requests
- Caching: Consider SQLite or JSON for frequently-accessed movies
- Async: Use `httpx` for parallel requests (within rate limits)

## File Structure

```
.
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization
│   ├── justwatch/               # JustWatch API client (to implement)
│   ├── letterboxd/              # Letterboxd API client (to implement)
│   └── web/                     # Web application interface (to implement)
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_justwatch.py        # JustWatch API validation
│   └── test_letterboxd.py       # Letterboxd API validation
├── .env.example                 # Environment template
├── pyproject.toml               # uv configuration
└── README.md                    # User documentation
```

## Current Development Goal

**Goal 1: API Access & Basic Integration Testing** ✅ COMPLETED

- [x] JustWatch API access validated (3/3 Netflix titles verified)
- [x] Letterboxd API access validated (3/3 movies + user profile verified)
- [x] Test scripts created and verified
- [x] API constraints documented
- [x] `.env.example` created
- [x] Project reorganized into modular structure

**Goal 2: Core Integration** 
- [ ] Implement JustWatch client wrapper (`src/justwatch/`)
- [ ] Implement Letterboxd client wrapper (`src/letterboxd/`)
- [ ] Build movie matching logic (IMDb ID-based)
- [ ] Add caching layer (SQLite or JSON)
- [ ] Write integration tests

**Goal 3: Web Interface** 
- [ ] Set up web framework (Flask/FastAPI)
- [ ] Create API endpoints for movie search and filtering
- [ ] Build frontend UI for streaming service selection
- [ ] Add filtering by genre, rating, year
- [ ] Deploy as public website

## Important Notes

- **Legal**: Ensure compliance with JustWatch and Letterboxd Terms of Service
- **Rate Limits**: Both services - use 1-2 second delays
- **Data Privacy**: Follow security best practices for any user data
- **Regional Settings**: Allow users to specify country for accurate availability

## Resources

- **JustWatch API Library**: https://github.com/Electronic-Mango/simple-justwatch-python-api
- **Letterboxd API Library**: https://pypi.org/project/letterboxdpy/
- **JustWatch Website**: https://www.justwatch.com/
- **Letterboxd Website**: https://letterboxd.com/
