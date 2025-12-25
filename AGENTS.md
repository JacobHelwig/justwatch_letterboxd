# AGENTS.md

This file provides guidance to agents (i.e., ADAL) when working with code in this repository.

## Project Overview

**justwatch_letterboxd** - A tool to integrate JustWatch streaming availability data with Letterboxd movie lists.

**Current Status**: Empty repository - project structure and implementation pending.

## Project Intent

Based on the repository name, this project likely aims to:
- Fetch movie data from JustWatch (streaming availability across platforms)
- Cross-reference with Letterboxd user data (watchlists, ratings, reviews)
- Provide streaming availability for movies in Letterboxd lists
- Possibly automate discovery of where to watch films from your Letterboxd collection

## Development Setup (To Be Determined)

Once the project structure is established, document here:
- **Language/Framework**: TBD (likely Python given typical API integration projects)
- **Package Manager**: TBD (poetry, pip, npm, etc.)
- **Dependencies**: TBD
- **API Keys Required**: 
  - JustWatch API credentials (if available)
  - Letterboxd API access (if using official API vs scraping)
- **Environment Variables**: Document in `.env.example` when created

## Essential Commands (Placeholder)

```bash
# To be filled in once project structure exists
# Example structure:
# poetry install              # Install dependencies
# poetry run python main.py   # Run main script
# poetry run pytest           # Run tests
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
├── pyproject.toml        # Python dependencies (if using Poetry)
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
   - Initialize package manager (poetry recommended for Python projects)
   - Create virtual environment
   - Set up linting (black, ruff) and testing (pytest)
   - Configure pre-commit hooks

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
