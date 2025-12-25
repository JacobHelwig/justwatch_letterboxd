# AGENTS.md

This file provides guidance to agents (i.e., ADAL) when working with code in this repository.

## Project Overview

**justwatch_letterboxd** - A tool to integrate JustWatch streaming availability data with Letterboxd movie lists.

**Current Status**: Empty repository - project structure and implementation pending.

## Project Intent

JustWatch is a popular service that aggregates streaming availability for movies and TV shows across various platforms such as Netflix and Hulu. Letterboxd is a social platform for film enthusiasts to track and review movies. This project aims to allow users to look at Letterboxd scores for movies that are available on their streaming platform of choice via JustWatch.

The base user workflow would be:
1. User selects their streaming services.
2. Our tool fetches movies available on this service from JustWatch and includes Letterboxd ratings for those movies.
3. The user can filter based on information from JustWatch and Letterboxd.


## Development Setup 

Once the project structure is established, document here:
- **Language/Framework**: python
- **Package Manager**: uv
- **Dependencies**: TBD
- **API Keys Required**: 
  - JustWatch API credentials (if available)
  - Letterboxd API access (if using official API vs scraping)
- **Environment Variables**: Document in `.env.example` when created

## Essential Commands

```bash
# Initialize project (if not done yet)
uv init

# Add dependencies
uv add requests httpx pytest

# Run main script
uv run python src/main.py

# Run tests
uv run pytest

# Run linter
uv run ruff check .
```

## Architecture Considerations

When implementing this project, consider documenting:

### Data Flow
- How movie data is fetched from JustWatch
- How Letterboxd data is retrieved (API vs web scraping)
- Data matching strategy (TMDB IDs, IMDb IDs, or title/year matching)
- Caching strategy to avoid rate limits

### Key Integration Points
- JustWatch API endpoints and rate limits
- Letterboxd data access method
- Data storage (if persisting matched results)
- Output format (CLI, web interface, CSV, etc.)

### Critical Considerations
- **Rate Limiting**: Both services may have API rate limits
- **Data Accuracy**: Movie title matching can be tricky (international titles, year variations)
- **Authentication**: Secure handling of API keys and user credentials
- **Regional Availability**: JustWatch data varies by country/region

## File Structure (To Be Created)

Suggested structure to document once established:
```
.
├── src/                    # Main source code
│   ├── justwatch/         # JustWatch API integration
│   ├── letterboxd/        # Letterboxd data fetching
│   └── matcher/           # Logic to match movies between services
├── tests/                 # Test suite
├── config/                # Configuration files
├── .env.example          # Example environment variables
├── pyproject.toml        # Python dependencies (managed by uv)
└── README.md             # User-facing documentation
```

## Next Steps for Development

1. **Choose Implementation Approach**:
   - Pure Python CLI tool
   - Web application (Flask/FastAPI)
   - Browser extension
   - Mobile app

2. **Research APIs**:
   - JustWatch: No official public API (may need to reverse engineer or use third-party libraries)
   - Letterboxd: Official API exists but requires approval; alternative is scraping

3. **Define MVP Features**:
   - Input: Letterboxd username or exported CSV
   - Processing: Match movies with JustWatch data
   - Output: List of movies with streaming availability

4. **Set Up Development Environment**:
   - Initialize package manager: `uv init`
   - Add core dependencies: `uv add requests httpx`
   - Set up linting: `uv add --dev ruff black`
   - Set up testing: `uv add --dev pytest`

## Important Notes

- **Legal Considerations**: Ensure compliance with JustWatch and Letterboxd Terms of Service
- **Respect Rate Limits**: Implement exponential backoff and caching
- **Data Privacy**: If handling user credentials, follow security best practices
- **Regional Settings**: Allow users to specify their country for accurate streaming availability

## Resources

- JustWatch unofficial API: Research community libraries
- Letterboxd API: https://letterboxd.com/api-coming-soon/
- Alternative: Letterboxd data export feature for CSV-based approach

---

**Note**: This AGENTS.md should be updated as the project structure evolves. Remove placeholder sections and add concrete commands, architecture details, and gotchas as they're discovered during development.
