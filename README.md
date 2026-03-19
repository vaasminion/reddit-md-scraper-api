# reddit-md-scraper-api

A REST API that scrapes posts and comments from any Reddit subreddit and returns the content as a Markdown file.

## Features

- Scrape posts and nested comments from any subreddit
- Filter by category — `best`, `hot`, `new`, `top`
- Returns a structured Markdown file with title, author, body, and comments
- Files organized by date on the server
- API key authentication support
- Detailed logging with traceid per request
- Dockerized and ready to deploy

## Project Structure

```
reddit-md-scraper-api/
├── api.py              # Entry point
├── auth/               # API key authentication
├── config/             # Constants and env config
├── logger/             # Logger setup
├── scraper/            # Reddit scraping logic
├── resources/          # Flask REST resource
├── utils/              # Utility functions
├── logs/               # Daily log files (auto-created)
├── mdfiles/            # Scraped markdown output (auto-created)
├── Dockerfile
└── docker-compose.yaml
```

## Requirements

- Docker & Docker Compose
- Or Python 3.10+

## Running with Docker

```bash
docker-compose up --build
```

With authentication enabled:
```bash
export REDDIT_SCRAPER_API_KEY=your-secret-key
docker-compose up --build
```

## Running Locally

```bash
pip install -r requirements.txt
python api.py
```

## API Usage

### `POST /scrape`

Scrapes a subreddit and returns a `.md` file.

**Headers**

| Header | Required | Description |
|---|---|---|
| `X-API-Key` | Only if auth enabled | Your API key |
| `Content-Type` | Yes | `application/json` |

**Request Body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `subreddit` | string | Yes | — | Subreddit name e.g. `python` |
| `category` | string | No | `best` | `best` / `hot` / `new` / `top` |
| `traceid` | string | No | auto-generated | Custom trace ID for logging |

**Example**

```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"subreddit": "python", "category": "hot"}' \
  --output reddit_python.md
```

**Response**

Returns the `.md` file as a download with `Content-Type: text/markdown`.

**Error Response**

```json
{ "error": "error message" }
```

## Authentication

Authentication is optional and controlled via an environment variable.

| `REDDIT_SCRAPER_API_KEY` set | Behaviour |
|---|---|
| Not set | Open access — no key required |
| Set | All requests must include `X-API-Key` header |

## Output Format

### File Name

Downloaded files follow this naming format:

```
reddit_scrape_{category}_{traceid}_{YYYYMMDD_HHMMSS}.md
```

Example:
```
reddit_scrape_best_A1B2C_20260315_143000.md
```

Files are also saved on the server under:
```
mdfiles/
└── YYYYMMDD/
    └── reddit_scrape_{category}_{traceid}_{YYYYMMDD_HHMMSS}.md
```

### File Content

The downloaded Markdown file is structured as:

```
REDDIT SCRAPE TIME UTC: 2026-03-15 14:30:00 UTC
[CATEGORY] :: best
[TITLE] :: Post title here
[AUTHOR_NAME] :: username
[URL] :: https://www.reddit.com/r/...
[BODY] :: Post body content
[COMMENTS] ::
👤 author: comment text

  --👤 nested_author: nested reply
```

## Environment Variables

| Variable | Description |
|---|---|
| `REDDIT_SCRAPER_API_KEY` | API key for authentication. Leave unset for open access. |

## Logging

Logs are written to both console and a daily log file in the `logs/` directory:

```
logs/
└── app_YYYY-MM-DD.log
```

Each request is tagged with a `traceid` for easy tracing across log lines.
