# AGENTS.md

This file provides guidance to agents (i.e., ADAL) when working with code in this repository.

## Project Overview

**justwatch_letterboxd** - A web application that integrates JustWatch streaming availability data with Letterboxd movie ratings.

**Current Status**: Goal 3 in progress - Web interface implementation

## Project Intent

JustWatch aggregates streaming availability for movies across platforms (Netflix, Hulu, etc.). Letterboxd is a social platform for film ratings and reviews. This project allows users to view Letterboxd ratings for movies available on their selected streaming platforms via JustWatch.

**User Workflow**:
1. Select streaming services or search by title
2. App fetches available movies from JustWatch with Letterboxd ratings
3. Filter results by genre, rating, year

## Development Setup 

- **Language/Framework**: Python 3.14+, FastAPI
- **Package Manager**: uv
- **Dependencies**: simple-justwatch-python-api, letterboxdpy, httpx, pytest, fastapi, uvicorn
- **API Keys Required**: None (both APIs use unofficial methods)
- **Environment Variables**: See `.env.example`

## Essential Commands

```bash
# Install dependencies
uv sync

# Run web application
uv run uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload

# Run all tests
uv run pytest

# Run specific test with verbose output
PYTHONPATH=. uv run python tests/test_web_api.py --verbose

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Trigger full Netflix catalog sync (initial setup)
curl -X POST http://localhost:8000/api/sync/trigger

# Check sync status
curl http://localhost:8000/api/sync/status

# View missing Letterboxd titles
curl http://localhost:8000/api/sync/missing
```

## Development Workflow

**Branch-Based Development**:
- Always develop on feature branches (e.g., `adal/goal-2-core-integration`)
- Never commit directly to main
- Open PR for review before merging to main
- Delete branch after merging

**Pre-Commit Checklist**:
1. ✅ Tests pass (`uv run pytest`)
2. ✅ Linter clean (`uv run ruff check .`)
3. ✅ Docs updated (README.md, AGENTS.md reflect changes, no outdated info)
4. ✅ Commit message descriptive with co-authorship

**Git Commit Co-Authorship**:
All commits made by AdaL should include co-authorship line at the end of commit message:
```
Co-Authored-By: AdaL <adal@sylph.ai>
```

**Incremental Development**:
- Commit changes incrementally after each logical unit of work
- Run tests after each implementation before committing
- Never commit broken code or failing tests

**Documentation Maintenance**:
- Update `README.md` and `AGENTS.md` after completing features or milestones
- Remove outdated information and correct inaccuracies when discovered
- Keep documentation synchronized with actual implementation

**Command Approval**:
AdaL uses `skip_approval=true` for all operations (read-only and write/modify). This allows seamless automation of tasks like git commits, PR creation, and file modifications without manual approval prompts.

**Testing Requirements**:
- All new features must include tests when feasible
- Tests should cover core functionality and edge cases
- Run tests before committing to ensure they pass
- Test files should be named `test_*.py` and placed in `tests/` directory
- All test files must include verbose mode support:
  - Add `--verbose` or `-v` flag to main() function
  - Print detailed output when verbose flag is provided
  - Show function return values and intermediate results
  - Usage: `PYTHONPATH=. uv run python tests/test_*.py --verbose`

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
### Integration Strategy

**Movie Matching**:
- Primary: IMDb ID matching (both APIs provide)
- Fallback: Title + year matching (less reliable)

**Caching**:
- SQLite database (`.cache/movies.db`)
- 24-hour default expiration
- Automatic caching on search/platform queries

**Performance**:
- Rate limiting: 1-2 second delays between requests
- Caching reduces repeated API calls by 90%

## File Structure

```
.
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization
│   ├── justwatch/               # JustWatch API client wrapper
│   ├── letterboxd/              # Letterboxd API client wrapper
│   ├── matcher.py               # Movie matching logic (IMDb ID-based)
│   ├── cache.py                 # SQLite caching layer
│   └── web/                     # Web application (FastAPI + frontend)
│       ├── app.py               # FastAPI application
│       ├── static/              # CSS and JavaScript
│       └── templates/           # HTML templates
├── tests/                       # Test suite (56 tests)
│   ├── test_justwatch_client.py # JustWatch wrapper tests
│   ├── test_letterboxd_client.py # Letterboxd wrapper tests
│   ├── test_matcher.py          # Matching logic tests
│   ├── test_cache.py            # Cache layer tests
│   ├── test_integration.py      # End-to-end tests
│   └── test_web_api.py          # Web API tests
├── .env.example                 # Environment template
├── pyproject.toml               # uv configuration
└── README.md                    # User documentation
```
## Development Goals

**Goal 1: API Access & Basic Integration Testing** ✅ COMPLETED
- JustWatch and Letterboxd API integration validated
- Test scripts created and verified

**Goal 2: Core Integration** ✅ COMPLETED
- JustWatch client wrapper (`src/justwatch/client.py`)
- Letterboxd client wrapper (`src/letterboxd/client.py`)
- Movie matching logic with IMDb ID-based matching (`src/matcher.py`)
- SQLite caching layer (`src/cache.py`)
- Integration tests (43 tests passing)

**Goal 3: Web Interface** 🚧 IN PROGRESS
- [x] FastAPI backend with REST API endpoints
- [x] Frontend UI (HTML, CSS, JavaScript)
- [x] Performance profiling and Letterboxd rating sorting
- [ ] Netflix catalog scraper (JustWatch website)
- [ ] Daily background sync job
- [ ] Developer logging for missing Letterboxd titles
- [ ] Docker containerization
- [ ] Deployment to cloud hosting

**Goal 4: Netflix-Focused Catalog Management** 📋 PLANNED
- [ ] Web scraper for JustWatch Netflix page (~7K titles)
- [ ] Catalog comparison logic (new/removed/retained titles)
- [ ] Daily background sync job (APScheduler/Celery)
- [ ] Developer logs for movies not found on Letterboxd
- [ ] Cache optimization (48h expiration, differential updates)
- [ ] Sync status API endpoint (`GET /api/sync/status`)
- [ ] Missing movies export (`GET /api/sync/missing`)

## Future Work / TODOs

**Testing & CI/CD**:
- [ ] Migrate all tests to pytest framework exclusively (currently using mix of pytest and custom main functions)
- [ ] Set up GitHub Actions CI/CD pipeline for automated testing
- [ ] Add test coverage reporting
- [ ] Configure automated PR checks (linting, tests, coverage)

**Performance & Scalability**:
- [ ] Concurrent API calls for Letterboxd (reduce from 2s/movie to batch processing)
- [ ] Background cache warming for popular movies
- [ ] Progress indicators for long-running operations
- [ ] Pagination support for large result sets

## Important Notes

- **Legal**: Ensure compliance with JustWatch and Letterboxd Terms of Service
- **Rate Limits**: Both services - use 1-2 second delays
- **Data Privacy**: Follow security best practices for any user data
- **Regional Settings**: Currently US-focused, allow users to specify country for accurate availability
- **Web Scraping**: JustWatch website scraping should be respectful (once daily at 2 AM)
## Resources

- **JustWatch API Library**: https://github.com/Electronic-Mango/simple-justwatch-python-api
- **Letterboxd API Library**: https://pypi.org/project/letterboxdpy/
- **JustWatch Website**: https://www.justwatch.com/
- **Letterboxd Website**: https://letterboxd.com/
