# ProductTracker

A backend system for tracking product prices across multiple e-commerce websites. Users submit a product URL, the system scrapes and stores the data, and automated background workers refresh prices daily without blocking API requests.

## Stack

- **FastAPI** — async REST API
- **PostgreSQL** — relational database
- **SQLAlchemy** — async ORM
- **Alembic** — schema migrations
- **Celery + Celery Beat** — distributed task queue and scheduler
- **Redis** — message broker and response cache
- **Docker + Docker Compose** — containerized multi-service deployment

## Architecture

- **Factory Pattern scraper** — config-driven CSS selectors per domain, extensible to new stores without writing new logic
- **Many-to-many user-product schema** — a product is stored once regardless of how many users track it, eliminating redundant scraping
- **Celery workers** — scraping is offloaded to background workers so POST /products returns immediately
- **Celery Beat** — triggers daily price refresh jobs across all tracked products
- **Redis cache** — GET /products responses are cached, reducing database load

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT | No |
| POST | `/products` | Submit a URL to track | Yes |
| GET | `/products` | List all tracked products | No |
| GET | `/products/me` | List products tracked by current user | Yes |
| GET | `/products/{id}` | Get product detail | No |
| DELETE | `/products/me/{id}` | Stop tracking a product | Yes |

Full interactive docs available at `/docs` once running.

## Setup

### Prerequisites

- Docker
- Docker Compose

### Environment Variables

Create a `.env` file in the project root (or use the example.env):

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/tracker
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/tracker
POSTGRES_DB=tracker
REDIS_URL=redis://redis:6379/0

POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Run with Docker Compose

```bash
docker-compose up --build
```

This starts four services:
- `fastapi` on port `8000`
- `postgres` on port `5432`
- `redis` on port `6379`
- `celery` worker
- `celery-beat` scheduler

API will be available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### Run Locally (without Docker)

```bash
pip install -r requirements.txt

# Terminal 1
fastapi dev main.py

# Terminal 2
celery -A celery_app worker --loglevel=info

# Terminal 3
celery -A celery_app beat --loglevel=info
```

## Adding a New Store

Add a new entry to `scraper/config.py`:

```python
SCRAPERS = {
    "example-store.com": {
        "title": "h1.product-title",
        "price": "span.price",
        "image_url": "img.product-image"
    }
}
```

No other code changes needed.
# ProductTracker
