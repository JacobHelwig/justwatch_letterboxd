# JustWatch + Letterboxd Integration

Discover highly-rated movies on your favorite streaming platforms. Our web application combines JustWatch streaming availability with Letterboxd ratings to help you find the perfect movie to watch tonight.

## What We Offer

**A public website where you can**:
1. Select your streaming services (Netflix, Hulu, Amazon Prime, etc.)
2. Browse movies available on your platforms
3. See Letterboxd ratings and reviews for each movie
4. Filter by genre, rating, and year
5. Find hidden gems worth watching

## Features

- **Multi-Platform Support**: Search across 60+ countries and all major streaming services
- **Smart Matching**: Automatically matches movies between JustWatch and Letterboxd using IMDb IDs
- **Rich Metadata**: Movie ratings, genres, directors, and cast information
- **Real-Time Data**: Fresh streaming availability and rating data
- **No Account Required**: Browse and discover movies without signing up

## Project Status

🚧 **In Development**

- ✅ **Goal 1 Complete**: API integration validated (JustWatch + Letterboxd)
- ✅ **Goal 2 Complete**: Core integration with caching and matching logic
- 🔄 **Goal 3 In Progress**: Web interface with background catalog sync
- ⏳ **Goal 4 Planned**: Deploy public website with full feature set

## Quick Start

**For Developers**:
```bash
# Install dependencies
uv sync

# Run web application
uv run uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload

# Trigger initial Netflix catalog sync (~2.1 hours)
curl -X POST http://localhost:8000/api/sync/trigger

# Check sync progress
curl http://localhost:8000/api/sync/status
```

**Background Sync**:
- Automatic daily sync at 2:00 AM
- Only queries Letterboxd for new titles (~10-50/day)
- Progress bar shows real-time matching status
- Cache expires after 48 hours for freshness

## Coming Soon

- Browse trending movies on your streaming platforms
- Save favorite movies and create watchlists
- Get personalized recommendations based on your ratings
- Share movie lists with friends
- Mobile-responsive design

## Contributing

This project is developed with assistance from [AdaL](https://github.com/sylphai/adal-cli), an AI coding assistant.

For developers interested in contributing, see `AGENTS.md` for technical guidance.

## Legal

This website uses unofficial APIs for educational purposes:
- **JustWatch**: Unofficial GraphQL API (no affiliation with JustWatch)
- **Letterboxd**: Web scraping for public data (no affiliation with Letterboxd)
- **Rate Limiting**: Respects both services with appropriate delays
- **Terms of Service**: Users should comply with JustWatch and Letterboxd ToS

## License

MIT (to be added)
