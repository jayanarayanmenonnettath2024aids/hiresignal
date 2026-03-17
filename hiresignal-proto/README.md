# HireSignal - Offline Resume Screening Platform

A fully self-contained, offline-first resume screening system built with FastAPI, PostgreSQL, Redis, Celery, and React. Screen resumes using multi-signal NLP scoring (SBERT semantic, TF-IDF, skill taxonomy, YoE matching) with real-time progress tracking and export capabilities.

## Features

### Resume Screening
- **Bulk Upload**: PDF, DOCX, TXT, or ZIP files (up to 1000 files per batch)
- **Single Spot-Check**: Quick 1-resume screening in <3 seconds
- **Real-Time Progress**: WebSocket live updates during batch processing
- **Multi-Signal Scoring**: 4 complementary ML signals (semantic, TF-IDF, skills, experience)

### NLP Pipeline
- **Smart Text Extraction**: PDF (with 2-column layout fix), DOCX (paragraphs + tables), TXT (auto-encoding detection)
- **OCR Fallback**: Handles scanned/degraded PDFs with pytesseract
- **Language Detection**: Automatically detects resume language
- **Skill Extraction**: 1500+ skill taxonomy covering programming, web, ML/AI, data, cloud, mobile, security
- **YoE Parsing**: Extracts years of experience from text
- **Boilerplate Removal**: Strips HR jargon, contact info, company intros

### Anomaly Detection
- **Keyword Stuffing Detection**: Flags resumes with unnatural skill density
- **Blank Resume Detection**: Filters out empty/corrupted files
- **Multilingual Flag**: Alerts HR to non-English resumes
- **Duplicate Detection**: SHA256-based content hashing prevents re-processing
- **OCR Usage Tracking**: Shows which resumes required OCR fallback

### Job Description Analysis
- **Skill Extraction**: Required vs nice-to-have skills
- **Quality Scoring**: Assessment of JD clarity (0-1 scale)
- **Vague JD Detection**: Warns when JD lacks specificity
- **YoE Requirement Parsing**: Extracts minimum experience requirement

### Results & Feedback
- **Ranked Results**: Auto-sorted by final score, with role-based access
- **Score Breakdown**: View all 4 signals per resume with detailed explanations
- **Skill Gap Analysis**: See matched/missing skills per candidate
- **HR Feedback**: Shortlist/reject decisions with optional notes
- **CSV & Excel Export**: 
  - CSV: RFC 4180 compliant with all fields (0-100 scale)
  - Excel: 3 sheets (shortlist ranked, score breakdown, JD meta) with conditional formatting

### Analytics
- **Overview Stats**: Total jobs, resumes screened, average match score, quota tracking
- **Score Trends**: Last 100 results with timestamps
- **Skill Analytics**: Top matched and missing skills across all jobs

### Multi-Tenancy
- **Header-Based Auth**: Simple, demonstration-friendly tenant isolation
- **Per-Tenant Quotas**: Monthly resume-screening limits
- **User Roles**: HR and Admin roles with different permissions
- **Data Isolation**: All requests filtered by tenant_id via JWT payload

## Tech Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.111.0 |
| Async ORM | SQLAlchemy | 2.0.30 (asyncio) |
| Database | PostgreSQL | 15 |
| Task Queue | Celery | 5.4.0 |
| Broker & Cache | Redis | 7 |
| Migrations | Alembic | 1.13.1 |
| Validation | Pydantic | v2 |
| **NLP/ML** | **Description** | **Purpose** |
| SBERT | sentence-transformers (all-MiniLM-L6-v2) | Semantic matching (cosine similarity) |
| TF-IDF | scikit-learn | Content similarity scoring |
| NLP Processing | spaCy en_core_web_sm | Lightweight linguistic processing |
| PDF Extraction | pdfplumber | Text + layout analysis |
| Scanned PDFs | pdf2image + pytesseract | OCR fallback |
| DOCX Parsing | python-docx | Word document extraction |
| Language Detection | langdetect | Multi-language support |
| Skill Taxonomy | Custom 1500+ terms | Domain-specific matching |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18.2.0 |
| Language | TypeScript | Latest |
| Build Tool | Vite | 5.0.0 |
| Styling | TailwindCSS | v3 |
| State Management | Zustand | Latest |
| Server State | TanStack Query (React Query) | v5 |
| HTTP Client | Axios | Latest |
| Charts | Recharts | Latest |
| UI Components | Custom (Tailwind) | — |

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **File Storage**: Local disk (./data/uploads/)
- **Process Manager**: Supervisor (manual) or systemd (Linux)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Nginx (Port 80 or 5173 dev)            │
│         Routes /api/* to backend, /ws/* to WebSocket            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                      │
        v                                      v
┌──────────────────────┐            ┌──────────────────────┐
│  React Frontend      │            │   FastAPI Backend    │
│  (Port 5173 dev)     │            │   (Port 8000)        │
│                      │            │                      │
│ - Login/Dashboard    │            │ - Auth Router        │
│ - Job Management     │◄──────────►│ - Jobs Router        │
│ - Results Viewer     │   REST API  │ - Resumes Router     │
│ - Single Screen      │            │ - Feedback Router    │
│ - Analytics          │            │ - Export Router      │
└──────────────────────┘            │ - Analytics Router   │
                                    │ - WebSocket Router   │
                                    └─────────┬────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    v                         v                         v
          ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
          │  PostgreSQL 15   │     │   Redis 7        │     │ Celery Workers   │
          │                  │     │                  │     │                  │
          │ Tenants          │     │ - Task Broker    │     │ process_screening│
          │ Users            │     │ - Result Backend │     │ _job()           │
          │ Jobs             │     │ - Pub/Sub        │     │                  │
          │ Resumes          │     │   (WebSocket)    │     │ process_single   │
          │ Feedback         │     │                  │     │ _resume()        │
          │                  │     │                  │     │                  │
          └──────────────────┘     └──────────────────┘     └──────────────────┘
                    │                                              │
                    └──────────────────┬───────────────────────────┘
                                       │
                            ┌──────────v──────────┐
                            │  Local Disk Storage │
                            │ ./data/uploads/     │
                            │ - Resumes (PDFs)    │
                            │ - Reports (CSV/XLS) │
                            └─────────────────────┘
```

## Scoring Algorithm

HireSignal uses a **4-signal weighted scoring system**:

### Signal 1: Semantic Similarity (40% by default)
- Encodes JD and resume using SBERT (all-MiniLM-L6-v2)
- Computes cosine similarity: **score = 1 - distance**
- Captures semantic matching independent of keyword overlap
- **Best for**: Understanding role fit beyond exact skill names

### Signal 2: TF-IDF Similarity (25-30% by default)
- Builds term-frequency inverse-document-frequency vectors
- Compares JD and resume content vocabulary
- Normalized to [0, 1] via cosine similarity
- **Best for**: Matching content density and relevant terminology

### Signal 3: Skill Matching (20-25% by default)
- Extracts skills from JD and resume using 1500+ term taxonomy
- Computes: `matched_skills / required_skills`
- Neutral score (0.5) if JD has no extracted skills
- **Best for**: Direct technical capability assessment

### Signal 4: Years of Experience (10-15% by default)
- Extracts min YoE from JD (e.g., "5+ years" → 5)
- Detects YoE from resume (date parsing, explicit statements)
- Scoring:
  - ✅ `≥ required YoE` → 1.0 (fully qualified)
  - 📊 `75%+ of required` → 0.7 (capable)
  - ⚠️ `50%+ of required` → 0.4 (developing)
  - ❌ `< 50% of required` → 0.1 (junior)
  - Neutral score (0.5) if YoE missing
- **Best for**: Seniority matching

### Final Score
```
final_score = (semantic × w_semantic) 
            + (tfidf × w_tfidf) 
            + (skills × w_skills) 
            + (experience × w_experience)

All signals ∈ [0, 1], weights sum to 1.0
Result ∈ [0, 1] → displayed as 0-100 in UI
```

### Anomaly Penalties
- **Keyword Stuffing** (skill_density > 0.35): Caps final_score at 0.6
- **Blank Resume** (<100 chars): Rejected before scoring
- **Duplicate Content**: Skipped if SHA256(content) seen before in same job

## Quick Start

### Option 1: Docker Compose (Recommended)
Fastest way to run the entire stack.

**Prerequisites**:
- Docker 20.10+
- Docker Compose 2.0+
- 4GB available RAM
- 5GB disk space

**Steps**:
```bash
# Clone the repo
git clone <repo-url>
cd hiresignal-proto

# Start all services (postgres, redis, backend, worker, frontend, nginx)
docker-compose up

# On first run, seed the demo database (in another terminal)
docker-compose exec backend python scripts/seed_db.py
```

**Access**:
- **Frontend**: http://localhost (or http://localhost:5173 for Vite dev)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

**Demo Credentials**:
| Email | Password | Tenant |
|-------|----------|--------|
| hr@acme.com | demo1234 | Acme Corp (2 jobs, 20 resumes) |
| admin@acme.com | demo1234 | Acme Corp |
| hr@startup.com | demo1234 | Startup Labs (demo only) |

**Stopping**:
```bash
docker-compose down          # Stop all services
docker-compose down -v       # Stop AND delete volumes
```

### Option 2: Manual Setup (3 Terminals)

**Prerequisites**:
- Python 3.11+
- Node.js 18+
- PostgreSQL 15 running (or `docker run -d -e POSTGRES_PASSWORD=postgres postgres:15`)
- Redis 7 running (or `docker run -d -p 6379:6379 redis:7`)
- Tesseract installed (`apt install tesseract-ocr` or `brew install tesseract`)

**Terminal 1 - Backend**:
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (create tables)
alembic upgrade head

# Seed demo data
python scripts/seed_db.py

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker**:
```bash
cd backend

# Activate the same venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend**:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Access at http://localhost:5173
```

## Configuration

### Environment Variables

Create a `.env` file at the project root or use `.env.example`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hiresignal
SYNC_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hiresignal

# Redis (Celery)
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_EXPIRY_HOURS=24

# Storage
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE_BYTES=52428800  # 50 MB
MAX_FILES_PER_UPLOAD=100

# Quotas
MONTHLY_QUOTA_ACME_CORP=5000
MONTHLY_QUOTA_STARTUP_LABS=500

# Features
DEBUG=False
ENVIRONMENT=development
```

### Celery Configuration

Edit `backend/app/workers/celery_app.py` to customize:

```python
# Queues (routing)
celery_app.conf.task_routes = {
    'app.workers.tasks.screening.process_single_resume': {'queue': 'critical'},
    'app.workers.tasks.screening.process_screening_job': {'queue': 'default'},
}

# Timeouts
TASK_SOFT_TIME_LIMIT = 3300  # 55 min soft
TASK_TIME_LIMIT = 3600       # 60 min hard
TASK_ACKS_LATE = True
PREFETCH_MULTIPLIER = 1       # One task per worker at a time
```

### Scoring Weights

Per-job weight configuration (via POST /api/jobs):

```json
{
  "title": "Senior Python Backend Engineer",
  "jd_text": "...",
  "weights": {
    "weight_semantic": 0.40,
    "weight_tfidf": 0.30,
    "weight_skills": 0.20,
    "weight_experience": 0.10
  }
}
```

Default weights sum to 1.0. Customize based on role criticality.

## API Reference

### Authentication
```
POST /api/auth/login
  Request:  { email: string, password: string }
  Response: { access_token: string, token_type: string }

GET /api/auth/me
  Headers: Authorization: Bearer {token}
  Response: { id, email, full_name, role, tenant_id }
```

### Jobs
```
POST /api/jobs
  { title, jd_text, weights: {...}, top_n: 100 }
  Response: { id, title, quality_score, is_vague, status, ... }

GET /api/jobs
  Response: Job[]

GET /api/jobs/{job_id}
  Response: Job

POST /api/jobs/preview-jd
  Form: jd_text
  Response: { skills, quality_score, is_vague, min_yoe }

POST /api/jobs/{job_id}/upload
  Multipart: files[]
  Response: { uploaded, skipped, files }

GET /api/jobs/{job_id}/results?skip=0&limit=100
  Response: ResumeResult[]

GET /api/jobs/{job_id}/summary
  Response: { job_id, status, counts, avg_score, ... }
```

### Resume Screening
```
POST /api/screen/single
  Form: jd_text, resume_file
  Response: { final_score, score_semantic, score_tfidf, score_skills, 
              score_experience, matched_skills[], missing_skills[], flags }
  Timeout: 10 seconds (synchronous wait for Celery task)
```

### Feedback
```
POST /api/feedback
  { result_id, action: "shortlist"|"reject", notes? }
  Response: { id, created_at, ... }

GET /api/feedback/job/{job_id}
  Response: Feedback[]
```

### Export
```
GET /api/export/{job_id}/csv
  Response: FileResponse (text/csv)

GET /api/export/{job_id}/excel
  Response: FileResponse (application/vnd.openxmlformats...)
```

### Analytics
```
GET /api/analytics/overview
  Response: { total_jobs, total_resumes_screened, avg_match_score, quota_used }

GET /api/analytics/score-trend
  Response: [{ date, score }, ...]

GET /api/analytics/skills
  Response: { top_matched_skills, top_missing_skills }
```

### WebSocket
```
WS /ws/jobs/{job_id}
  Receives: { processed, total, status, latest: {filename, score} }
  Broadcasts on Redis channel: job:{job_id}:progress
```

## Database Schema

### Core Tables
- **tenants**: Company/account records with quotas
- **users**: HR and admin users per tenant
- **screening_jobs**: Job openings with JD + scoring config
- **resume_results**: Screening outcomes (scores, skills, flags)
- **hr_feedback**: Shortlist/reject decisions

### Key Relationships
```
Tenant (1) ──→ (many) User
Tenant (1) ──→ (many) ScreeningJob
ScreeningJob (1) ──→ (many) ResumeResult
ResumeResult (1) ──→ (many) HRFeedback
```

All tables include `tenant_id` for multi-tenancy isolation.

## File Storage

Local disk layout:
```
./data/uploads/
├── {tenant_id}/
│   ├── resumes/
│   │   └── {job_id}/
│   │       ├── {hash}_{original_filename}.pdf
│   │       ├── {hash}_{original_filename}.docx
│   │       └── ...
│   └── reports/
│       ├── {job_id}.csv
│       └── {job_id}.xlsx
```

Path validation prevents directory traversal (`..` is rejected).

## Deployment

### Production Checklist
- [ ] .env: Change `JWT_SECRET_KEY` to random 32+ char string
- [ ] .env: Set `DEBUG=False`
- [ ] Database: Run `alembic upgrade head` migrations
- [ ] Database: Seed initial users `python scripts/seed_db.py`
- [ ] Storage: Ensure `./data/uploads` has 777 permissions
- [ ] Redis: Password-protect if exposed
- [ ] Nginx: Enable SSL/TLS (add .crt/.key files)
- [ ] CORS: Restrict origins in FastAPI (not * for production)
- [ ] Logging: Configure centralized log aggregation (Sentry, CloudWatch)

### Docker Production Build
```bash
# Build optimized images
docker-compose -f docker-compose.yml build

# Run with resource limits
docker-compose up -d --scale worker=3   # 3 Celery workers for scale
```

### Manual Production (Systemd)

**Create `/etc/systemd/system/hiresignal-backend.service`**:
```ini
[Unit]
Description=HireSignal FastAPI Backend
After=network.target

[Service]
Type=notify
User=hiresignal
WorkingDirectory=/opt/hiresignal/backend
Environment="PATH=/opt/hiresignal/backend/venv/bin"
ExecStart=/opt/hiresignal/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Same pattern for Celery worker and frontend (with different ExecStart)**.

## Troubleshooting

### Docker Issues

**"dial tcp: lookup postgres: no such host"**
- Ensure `docker-compose up` completed without errors
- Check `docker compose ps` shows all 6 services running
- Verify networks: `docker network ls | grep hiresignal`

**"Redis connection refused"**
- Confirm Redis container is running: `docker compose logs redis`
- Check Redis port: `docker exec redis redis-cli ping` (should reply PONG)

### Import Errors

**"No module named 'sentence_transformers'"**
- Inside backend container: `pip install -r requirements.txt`
- Ensure Dockerfile runs `pip install`

**"No module named 'app'"**
- Check working directory in FastAPI is correct: `cd /app/backend && python -m app.main`

### Database Errors

**"FATAL: role 'postgres' does not exist"**
- Initialize PostgreSQL: `docker compose down -v && docker compose up postgres` first

**"relation 'tenant' does not exist"**
- Run migrations: `docker compose exec backend alembic upgrade head`

### Performance

**Slow screening on large batches (>500 resumes)**
- Scale Celery workers: `docker-compose up -d --scale worker=5`
- Increase Celery batch size: edit `BATCH_SIZE` in `screening.py`
- Pre-compute SBERT embedding: see `embeddings.py` for caching strategy

**High memory usage**
- Reduce SBERT batch size: `encode_batch(texts, batch_size=8)` (default 32)
- Disable debug mode: `DEBUG=False` in .env
- Clear old Redis keys: `redis-cli FLUSHDB`

## Development

### Project Structure
```
hiresignal-proto/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── services/        # Business logic
│   │   ├── routers/         # FastAPI endpoints
│   │   ├── nlp/             # NLP pipeline (7 modules)
│   │   ├── workers/         # Celery tasks
│   │   ├── utils/           # Helpers
│   │   ├── middleware/      # Tenant middleware
│   │   ├── main.py          # FastAPI entry point
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── config.py        # Environment settings
│   │   └── dependencies.py  # DI for auth
│   ├── alembic/             # Database migrations
│   ├── scripts/
│   │   └── seed_db.py       # Demo data
│   ├── requirements.txt     # Dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages (Dashboard, NewJob, etc.)
│   │   ├── components/      # Reusable React components
│   │   ├── api/             # Axios client + endpoints
│   │   ├── store/           # Zustand auth store
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx          # Router
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Tailwind
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── index.html
├── nginx/
│   └── nginx.conf           # Reverse proxy + SPA routing
├── docker-compose.yml       # All services orchestration
├── .env.example             # Configuration template
└── README.md                # This file
```

### Adding a New Endpoint

1. **Define Schema** (`backend/app/schemas/`):
```python
class MyRequestSchema(BaseModel):
    field: str
```

2. **Create Service Method** (`backend/app/services/my_service.py`):
```python
async def process_something(self, data: MyRequestSchema):
    return result
```

3. **Add Route** (`backend/app/routers/my_router.py`):
```python
@router.post('/api/something')
async def create_something(
    req: MyRequestSchema,
    user_id = Depends(get_current_user_id),
    tenant_id = Depends(get_current_tenant_id)
):
    return await service.process_something(req)
```

4. **Update Frontend Client** (`frontend/src/api/client.ts`):
```typescript
somethingAPI: {
  create: (data) => api.post('/something', data),
}
```

5. **Use in React Page**:
```typescript
const { mutate } = useMutation({
  mutationFn: somethingAPI.create,
  onSuccess: () => queryClient.invalidateQueries(['something']),
})
```

### Running Tests

```bash
# Backend pytest (add `pytest` to requirements.txt first)
cd backend
pytest app/

# Frontend Jest
cd frontend
npm run test
```

### Code Style

**Python**:
- Format: `black .`
- Lint: `pylint app/`
- Type hints: Use Python 3.11+ syntax

**TypeScript/React**:
- Format: `prettier --write src/`
- Lint: `npm run lint`
- Components: Functional + hooks

## Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/my-feature`
5. Open PR

## License

MIT License - see LICENSE.md

## Support

- **Issues**: GitHub Issues
- **Docs**: See README.md and API docs (/docs endpoint)
- **Email**: support@hiresignal.dev

## Changelog

### v1.0.0 (Current Release)
- ✅ Full 4-signal NLP scoring
- ✅ Batch processing with live progress
- ✅ 2-column PDF + OCR support
- ✅ 1500+ skill taxonomy
- ✅ Anomaly detection (stuffing, blank, multilingual)
- ✅ CSV + Excel export with formatting
- ✅ Multi-tenancy with JWT auth
- ✅ Docker Compose deployment
- ✅ React admin dashboard

### Roadmap
- [ ] OAuth2 / SAML integration
- [ ] MinIO S3-compatible storage option
- [ ] Prometheus/Grafana monitoring
- [ ] Webhook integrations (Slack, email)
- [ ] Advanced filtering (saved searches)
- [ ] Team collaboration (notes, assignments)
- [ ] Custom scoring rules (drag-drop weights)
- [ ] API rate limiting
- [ ] Audit logs

---

**Built with ❤️ for efficient hiring**
