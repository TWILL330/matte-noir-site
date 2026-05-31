# Kantata Reddit Intelligence

Internal tool for identifying Kantata-fit companies, buyer roles, pain points,
competitor mentions, and purchase-intent signals from Reddit-derived data.

## Tech stack

| Layer     | Technology                                    |
|-----------|-----------------------------------------------|
| Frontend  | Next.js 14 (App Router, Tailwind CSS)         |
| Backend   | FastAPI + Uvicorn                             |
| Database  | PostgreSQL 16                                 |
| Cache     | Redis 7                                       |
| ORM       | SQLAlchemy 2 + Alembic                        |

---

## Prerequisites

- Docker + Docker Compose **or** Python 3.12+, Node 20+, PostgreSQL 16, Redis 7

---

## Quick start with Docker

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd matte-noir-site

# 2. Copy environment file
cp .env.example .env

# 3. Build and start all services
docker compose up --build -d

# 4. Run database migrations
docker compose exec api alembic upgrade head

# 5. Seed the taxonomy vocabulary
docker compose exec api python seed.py

# 6. Open the app
#   Dashboard → http://localhost:3000
#   API docs  → http://localhost:8000/docs
```

---

## Local development (no Docker)

### Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kantata_reddit
export REDIS_URL=redis://localhost:6379/0

# Create the database first if needed:
# createdb kantata_reddit

alembic upgrade head
python seed.py

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

npm install

echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
# → http://localhost:3000
```

---

## Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "describe the change"

# Roll back one step
alembic downgrade -1
```

---

## Seed the taxonomy

```bash
# From backend/
python seed.py
```

Seeds industries, buyer roles, pain points, competitors, and intent stages.
Safe to re-run — existing terms are skipped.

---

## Importing data

### Via the UI

1. Go to **http://localhost:3000/import**
2. Upload a `.csv` or `.json` file (max 50 MB)
3. Records are normalized → tagged → scored automatically

### Via the API

```bash
curl -X POST http://localhost:8000/import \
  -F "file=@sample_data/sample_posts.csv"
```

### Expected CSV columns

| Column         | Notes                                                     |
|----------------|-----------------------------------------------------------|
| `id`           | Reddit ID; auto-generated from content hash if missing    |
| `source_type`  | `post` or `comment`; inferred from `title` if missing     |
| `subreddit`    | With or without `r/` prefix                              |
| `author`       | Username                                                  |
| `title`        | Present for posts; absent for comments                   |
| `body`         | Also aliased as `selftext`, `text`, `content`            |
| `url`          | Also aliased as `permalink`, `link`                      |
| `created_utc`  | Unix timestamp or ISO 8601                               |
| `score`        | Reddit upvote count; also aliased as `upvotes`, `ups`    |
| `num_comments` | Also aliased as `comment_count`, `comments`              |

At least one of `title` or `body` must be non-empty or the row is skipped.

See `sample_data/sample_posts.csv` and `sample_data/sample_posts.json` for
working examples.

---

## Scoring reference

All scores are integers **0–100**.

| Dimension        | ABM weight | What it measures                                         |
|------------------|-----------|----------------------------------------------------------|
| ICP Fit          | 35%       | Industry, buyer role, and subreddit match with Kantata ICP |
| Pain Severity    | 30%       | Acuteness and urgency of expressed pain points           |
| Purchase Intent  | 35%       | Intent stage, competitor mentions, evaluation language   |
| **ABM Priority** | —         | Weighted composite of the three dimensions above         |

---

## API reference

| Method | Path                  | Description                            |
|--------|-----------------------|----------------------------------------|
| GET    | `/health`             | Health check                           |
| POST   | `/import`             | Upload CSV or JSON file                |
| GET    | `/records`            | List records (search + filter + page)  |
| GET    | `/records/facets`     | Available filter values for dropdowns  |
| GET    | `/records/{id}`       | Single record with tags and scores     |
| GET    | `/export`             | Download filtered records as CSV       |

Interactive docs: **http://localhost:8000/docs**

### Record list query params

| Param               | Type    | Description                                |
|---------------------|---------|--------------------------------------------|
| `q`                 | string  | Full-text search on title and body         |
| `subreddit`         | string  | Exact subreddit match                      |
| `industry`          | string  | Filter by industry tag                     |
| `buyer_role`        | string  | Filter by buyer role tag                   |
| `pain_point`        | string  | Filter by pain point tag                   |
| `competitor`        | string  | Filter by competitor mention               |
| `intent_stage`      | string  | `awareness` / `consideration` / `decision` / `frustration` / `advocacy` |
| `min_icp_fit`       | int     | Minimum ICP Fit score (0–100)              |
| `min_pain_severity` | int     | Minimum Pain Severity score                |
| `min_purchase_intent`| int   | Minimum Purchase Intent score              |
| `min_abm_priority`  | int     | Minimum ABM Priority score                 |
| `page`              | int     | Page number, 1-indexed (default: 1)        |
| `page_size`         | int     | Records per page, max 100 (default: 20)    |

---

## Project structure

```
matte-noir-site/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS + lifespan
│   │   ├── config.py            # Pydantic-settings env config
│   │   ├── database.py          # SQLAlchemy engine + get_db
│   │   ├── cache.py             # Redis client
│   │   ├── models/              # ORM models (7 tables)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── providers/
│   │   │   ├── base.py          # RedditDataProvider ABC + PROVIDER_REGISTRY
│   │   │   └── manual_import.py # ManualImportProvider (CSV + JSON)
│   │   ├── services/
│   │   │   ├── normalizer.py    # Field aliasing + type coercion
│   │   │   ├── tagger.py        # Keyword-based enrichment (5 dimensions)
│   │   │   └── scorer.py        # Rule-based 0–100 scoring (4 dimensions)
│   │   ├── routers/
│   │   │   ├── import_.py       # POST /import
│   │   │   ├── records.py       # GET /records, /records/facets, /records/{id}
│   │   │   └── export.py        # GET /export
│   │   └── seeds/
│   │       └── taxonomy_seed.py # Controlled vocabulary data
│   ├── migrations/              # Alembic migration files
│   ├── seed.py                  # Taxonomy seed runner
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages (dashboard, import, record detail)
│       ├── components/          # UI components
│       └── lib/                 # API client + TypeScript types
├── sample_data/                 # 10 realistic sample records (CSV + JSON)
├── docker-compose.yml
└── .env.example
```

---

## Adding a new data provider

1. Create `backend/app/providers/my_provider.py`
2. Subclass `RedditDataProvider` and implement `fetch()`
3. Register it: `PROVIDER_REGISTRY["my_provider"] = MyProvider`

Raw dicts from `fetch()` are passed to `normalizer.normalize()` which handles
all field aliasing — providers don't need to conform to the internal schema.
