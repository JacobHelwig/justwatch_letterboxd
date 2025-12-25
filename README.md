# JustWatch + Letterboxd Integration

Discover highly-rated movies on your favorite streaming platforms by combining JustWatch streaming availability with Letterboxd ratings.

## What It Does

This tool helps you find movies to watch by:
1. **Select** your streaming service (Netflix, Hulu, etc.)
2. **Fetch** available movies from JustWatch for your region
3. **Enrich** with Letterboxd ratings and metadata
4. **Filter** by rating, genre, year, and more

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/JacobHelwig/justwatch_letterboxd.git
cd justwatch_letterboxd

# Install dependencies with uv
uv sync
```

### Configuration

Copy `.env.example` to `.env` and configure your preferences:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
JUSTWATCH_COUNTRY=US        # Your country code (US, GB, FR, etc.)
JUSTWATCH_LANGUAGE=en       # Language code
```

### Run Tests

```bash
# Test JustWatch API
uv run python tests/test_justwatch.py

# Test Letterboxd API
uv run python tests/test_letterboxd.py
```

## Project Status

**Current**: Goal 1 completed - API integration validated
- ✅ JustWatch API: Streaming availability fetching
- ✅ Letterboxd API: Movie ratings and metadata
- ✅ Test scripts verified with 100% success rate

**Next**: Goal 2 - Core integration (client wrappers, caching, matching logic)

## Features

### JustWatch Integration
- Search movies across 60+ countries
- Filter by streaming platform (Netflix, Hulu, Amazon Prime, etc.)
- Get offers by quality (4K, HD, SD)
- No authentication required

### Letterboxd Integration
- Movie ratings (1-5 scale)
- Genres, year, directors
- User profile data (public profiles only)
- No authentication required for public data

### Matching Strategy
- **Primary**: IMDb ID matching (most reliable)
- **Fallback**: Title + year matching

## Project Structure

```
.
├── src/                    # Main source code
│   ├── justwatch/         # JustWatch API client (planned)
│   ├── letterboxd/        # Letterboxd API client (planned)
│   └── cli/               # CLI interface (planned)
├── tests/                 # Test suite
│   ├── test_justwatch.py  # JustWatch API tests
│   └── test_letterboxd.py # Letterboxd API tests
├── docs/                  # Documentation
│   └── API_FINDINGS.md    # API test results
├── .env.example          # Environment template
└── AGENTS.md             # Developer guidance (for AdaL)
```

## Dependencies

- **Python**: 3.14+ (managed by uv)
- **JustWatch**: `simple-justwatch-python-api` (unofficial GraphQL client)
- **Letterboxd**: `letterboxdpy` (web scraping library)
- **HTTP**: `httpx` (async HTTP client)
- **Testing**: `pytest`

## Contributing

This project is developed with assistance from [AdaL](https://github.com/sylphai/adal-cli), an AI coding assistant.

Contributions welcome! See `AGENTS.md` for development guidance.

## Legal

- **JustWatch**: Uses unofficial GraphQL API (may break if schema changes)
- **Letterboxd**: Uses web scraping for public data (fragile to HTML changes)
- **Rate Limiting**: Respects both services with 1-2 second delays
- **Terms of Service**: Ensure compliance with JustWatch and Letterboxd ToS

## References

- [JustWatch](https://www.justwatch.com/)
- [Letterboxd](https://letterboxd.com/)
- [simple-justwatch-python-api](https://github.com/Electronic-Mango/simple-justwatch-python-api)
- [letterboxdpy](https://pypi.org/project/letterboxdpy/)

## License

MIT (to be added)
