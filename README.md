# reddit-md-scraper-api

A REST API that scrapes posts and comments from any Reddit subreddit and returns the content as a Markdown file.

## Features

- Scrape posts and nested comments from any subreddit
- Filter by category — `best`, `hot`, `new`, `top`
- Returns a structured Markdown file with title, author, body, and comments
- **v1** — lightweight scraper using Python's built-in `urllib`
- **v2** — enhanced scraper powered by [Scrapling](https://github.com/D4Vinci/Scrapling) with better anti-bot handling and built-in retry logic
- Files organized by date on the server
- API key authentication support
- Detailed logging with traceid per request
- Swagger UI for interactive API documentation
- Dockerized and ready to deploy

## Project Structure

```
reddit-md-scraper-api/
├── api.py              # Entry point — registers all endpoints + Swagger
├── auth/               # API key authentication
├── config/             # Constants and env config
├── logger/             # Logger setup
├── scraper/
│   ├── scraper.py      # v1 scraper (urllib)
│   └── scraper_v2.py   # v2 scraper (Scrapling)
├── resources/
│   ├── resources.py    # POST /scrape  (v1)
│   └── resources_v2.py # POST /v2/scrape (v2)
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

> The app is exposed on port **5002** (mapped to internal 5000).

## Running Locally

```bash
pip install -r requirements.txt
python api.py
```

## Swagger UI

Interactive API docs are available at:

```
http://localhost:5000/docs/
```

## API Usage

Both endpoints accept the same parameters and return the same output format. The difference is the underlying HTTP engine used for scraping.

---

### `POST /scrape` — v1

Uses Python's built-in `urllib`. Lightweight with no extra dependencies.

**Headers**

| Header | Required | Description |
|---|---|---|
| `X-API-Key` | Only if auth enabled | Your API key |

**Form Fields**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `subreddit` | string | Yes | — | Subreddit name e.g. `python` |
| `category` | string | No | `best` | `best` / `hot` / `new` / `top` |
| `traceid` | string | No | auto-generated | Custom trace ID for logging |

**Example**

```bash
curl -X POST http://localhost:5000/scrape \
  -H "X-API-Key: your-secret-key" \
  -F "subreddit=python" \
  -F "category=hot" \
  --output reddit_python.md
```

---

### `POST /v2/scrape` — v2 (Scrapling)

Uses [Scrapling](https://github.com/D4Vinci/Scrapling) as the HTTP engine. Provides better anti-bot fingerprinting, automatic retries, and rate-limit (429) handling.

**Headers**

| Header | Required | Description |
|---|---|---|
| `X-API-Key` | Only if auth enabled | Your API key |

**Form Fields**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `subreddit` | string | Yes | — | Subreddit name e.g. `python` |
| `category` | string | No | `best` | `best` / `hot` / `new` / `top` |
| `traceid` | string | No | auto-generated | Custom trace ID for logging |

**Example**

```bash
curl -X POST http://localhost:5000/v2/scrape \
  -H "X-API-Key: your-secret-key" \
  -F "subreddit=python" \
  -F "category=hot" \
  --output reddit_python_v2.md
```

---

**Response**

Both endpoints return the `.md` file as a download with `Content-Type: text/markdown`.

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

### File Naming

| Version | Format |
|---|---|
| v1 | `reddit_scrape_{category}_{traceid}_{YYYYMMDD_HHMMSS}.md` |
| v2 | `reddit_scrape_v2_{category}_{traceid}_{YYYYMMDD_HHMMSS}.md` |

Files are saved on the server under:
```
mdfiles/
└── YYYYMMDD/
    └── reddit_scrape[_v2]_{category}_{traceid}_{YYYYMMDD_HHMMSS}.md
```

### File Content

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
