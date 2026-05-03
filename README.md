# SanchaarSetu

> Bidirectional sync middleware for Karnataka's Single Window System — keeping 40+ legacy department systems in continuous alignment without touching any of them.

---

## Table of contents

- [What this is](#what-this-is)
- [Why it exists](#why-it-exists)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local setup](#local-setup)
- [Running the stack](#running-the-stack)
- [Core flows](#core-flows)
- [Configuration](#configuration)
- [Security model](#security-model)
- [Testing](#testing)
- [Onboarding a new department](#onboarding-a-new-department)
- [Hackathon demo guide](#hackathon-demo-guide)

---

## What this is

SanchaarSetu ("communication bridge" in Kannada) is a live, non-invasive sync layer that sits between Karnataka's Single Window System (SWS) and every department system it connects to — Factories, Labour, Fire Safety, BBMP, and 37 more.

It treats every system as an immutable black box. It never modifies source systems. It integrates around them through their existing APIs and event surfaces, translating payloads, resolving conflicts, and maintaining a tamper-evident audit trail of every change.

---

## Why it exists

Karnataka's SWS is the front door for business registrations across the state. Over 40 legacy department systems operate independently — built at different times, using different schemas, with no knowledge of each other.

The result is a **split-brain problem**:

- A business updates its address on SWS. The 40 department systems remain unaware.
- Each system develops its own version of the truth.
- Officers see conflicting records. Businesses receive notices at wrong addresses. License renewals fail due to stale signatory data.

A big-bang migration is not viable — the GST rollout proved this. Millions of records, heterogeneous schemas, and live operational dependencies make a hard cutover a guaranteed disaster.

SanchaarSetu is the only viable path: a live sync layer that keeps both sides aligned without requiring any changes to either.

The foundational precondition is the **UBID (Unified Business Identifier)** — the single common key that links a business's identity across all systems. Without UBID, there is no reliable way to match a SWS record to its counterpart in the Factories system. UBID makes interoperability solvable.

---

## How it works

SanchaarSetu operates in two directions simultaneously.

### SWS → Departments

```
SWS raises a service request (e.g., address change)
        ↓
Webhook listener receives the event
        ↓
Idempotency check (Redis) — skip if already processed
        ↓
PII scrubber tokenizes sensitive fields
        ↓
Event placed on Kafka topic: sws-to-dept
        ↓
Transform Engine maps SWS payload → each department's schema
        ↓
Conflict Resolver checks for concurrent updates on same UBID
        ↓
Adapter writes to each department via its existing API
        ↓
Audit store records the outcome for every destination
```

### Departments → SWS

Department systems were never designed to broadcast changes. SanchaarSetu's Ingestion Engine uses three tiers to detect them regardless:

| Tier | Method | Latency | Used when |
|------|--------|---------|-----------|
| 1 | Webhook | < 1 second | Department natively emits events |
| 2 | Polling | 1 – 15 min | Department has a read API but no event surface |
| 3 | Snapshot diff (Debezium) | Hourly | Database-level access only |

Once a change is detected, it follows the same pipeline in reverse — normalised, placed on Kafka, translated into the SWS schema, joined on UBID, and written to SWS via its existing API.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SanchaarSetu middleware                     │
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────────────────┐  │
│  │  Webhook listener │         │      Ingestion engine        │  │
│  │  (FastAPI)        │         │  Tier 1 / Tier 2 / Tier 3   │  │
│  └────────┬─────────┘         └─────────────┬────────────────┘  │
│           │                                 │                   │
│           ▼                                 ▼                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    PII scrubber                          │   │
│  │        Tokenizes before any AI or LLM call               │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Apache Kafka                           │   │
│  │  Topics: sws-to-dept │ dept-to-sws │ dead-letter-queue  │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                   │
│              ┌──────────────┼──────────────┐                    │
│              ▼              ▼              ▼                    │
│  ┌─────────────────┐ ┌────────────┐ ┌───────────────────┐      │
│  │ Transform Engine│ │  Conflict  │ │   UBID Registry   │      │
│  │ Sentence Transf.│ │  Resolver  │ │   + pgvector      │      │
│  │ + pgvector maps │ │ 3 policies │ │   (PostgreSQL)    │      │
│  └────────┬────────┘ └─────┬──────┘ └───────────────────┘      │
│           │               │                                     │
│           ▼               ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          Redis idempotency    │    Audit store           │   │
│  │          (dedup before write) │    (append-only PG)      │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────────┐
         ▼                 ▼                      ▼
   ┌──────────┐     ┌──────────┐          ┌──────────────┐
   │ Factories│     │  Labour  │   ...    │  BBMP + 37   │
   │  adapter │     │  adapter │          │   more       │
   └──────────┘     └──────────┘          └──────────────┘
```

### Component responsibilities

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| API layer | FastAPI (Python) | Webhook listener, REST endpoints for UI |
| Message queue | Apache Kafka | Durable ordered delivery, replay, DLQ |
| Change detection | Debezium + custom pollers | Covers CDC and polling-only department systems |
| Schema mapping | Sentence Transformers + pgvector | Semantic field matching; mappings learned once |
| Idempotency | Redis | Sub-millisecond dedup before every write |
| Audit + mapping store | PostgreSQL (append-only) | No-overwrite log; vector registry for mappings |
| Orchestration | Temporal.io | Stateful retries; survives crashes mid-propagation |
| PII handling | Custom pre-processor | No LLM inference on raw personal data, ever |
| Frontend | React + Vite + Tailwind | Dashboard, conflict review, mapping approval UI |

---

## Project structure

```
sanchaarsetu/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── webhook/
│   │   │   └── router.py            # SWS event listener + idempotency gate
│   │   ├── ingestion/
│   │   │   ├── tier1_webhook.py     # Dept webhook receivers
│   │   │   ├── tier2_poller.py      # Scheduled API polling
│   │   │   └── tier3_debezium.py    # Snapshot diff via Debezium
│   │   ├── transform/
│   │   │   ├── engine.py            # Sentence Transformer mapping + apply
│   │   │   └── worker.py            # Kafka consumer loop for transform
│   │   ├── conflict/
│   │   │   └── resolver.py          # 3-policy conflict resolution
│   │   ├── pii/
│   │   │   └── scrubber.py          # Regex tokenizer + restore
│   │   ├── audit/
│   │   │   └── writer.py            # Append-only writes + hash chaining
│   │   ├── adapters/
│   │   │   ├── registry.py          # UBID → department lookup
│   │   │   ├── factories.py         # Factories dept adapter
│   │   │   ├── labour.py            # Labour dept adapter
│   │   │   └── mock_dept.py         # Generic mock for demo
│   │   └── kafka_client.py          # Producer + consumer factory
│   ├── migrations/
│   │   └── 001_audit_log.sql        # Append-only table + REVOKE statements
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx        # Live sync event feed
│   │   │   ├── ConflictReview.jsx   # Manual conflict resolution UI
│   │   │   └── MappingRegistry.jsx  # Field mapping approval UI
│   │   ├── components/
│   │   │   ├── EventCard.jsx
│   │   │   ├── ConflictCard.jsx
│   │   │   └── MappingRow.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
│
├── infra/
│   ├── docker-compose.yml           # Full local stack
│   └── kafka/
│       └── topics.sh                # Topic creation script
│
├── mock_departments/
│   └── server.py                    # 3 mock dept APIs for demo
│
└── README.md
```

---

## Prerequisites

### System requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Disk | 10 GB free | 20 GB free |
| OS | macOS 12+, Ubuntu 22.04+, Windows 11 (WSL2) | macOS (Apple Silicon) |

### Required software

- **Python 3.10+** — `python --version`
- **Node.js 18+** — `node --version`
- **Docker Desktop** with Compose v2 — `docker compose version`
- **Git** — `git --version`
- **Homebrew** (macOS) — for native dependencies

### Apple Silicon (M1/M2/M3/M4) — additional notes

Confluent Kafka's Docker images are `amd64` only. Add `platform: linux/amd64` to the Kafka and Zookeeper services in `docker-compose.yml` — Docker will use Rosetta 2 transparently. Alternatively, replace Kafka with **Redpanda** which ships a native ARM image.

PyTorch on Apple Silicon should use the native MPS backend — not the Rosetta-emulated build. The setup script below handles this automatically.

---

## Local setup

### 1 — Clone the repository

```bash
git clone https://github.com/your-org/sanchaarsetu.git
cd sanchaarsetu
```

### 2 — Install system dependencies (macOS)

```bash
brew install pyenv librdkafka node git
```

`librdkafka` is required for `confluent-kafka` to compile natively on Apple Silicon. Without it, pip will fail.

### 3 — Set up Python environment

```bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv .venv
source .venv/bin/activate
```

### 4 — Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

`requirements.txt` contents:

```
fastapi
uvicorn[standard]
confluent-kafka
sentence-transformers
psycopg2-binary
sqlalchemy
redis
pgvector
python-dotenv
httpx
temporalio
```

### 5 — Verify MPS (Apple Silicon only)

```bash
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

Should print `MPS available: True`. If not, reinstall torch: `pip install --force-reinstall torch`.

### 6 — Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 7 — Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values — see [Configuration](#configuration) below.

---

## Running the stack

### Step 1 — Start infrastructure

```bash
cd infra
docker compose up -d
```

This starts: Kafka + Zookeeper, Redis, PostgreSQL (with pgvector extension).

Verify all containers are healthy:

```bash
docker compose ps
```

All services should show `Up` or `healthy`.

### Step 2 — Create Kafka topics

```bash
bash infra/kafka/topics.sh
```

This creates three topics:

```
sws-to-dept         (partitions: 3, replication: 1)
dept-to-sws         (partitions: 3, replication: 1)
dead-letter-queue   (partitions: 1, replication: 1)
```

### Step 3 — Run database migrations

```bash
docker exec -i sanchaarsetu-postgres-1 psql -U setu -d sanchaarsetu \
  < backend/migrations/001_audit_log.sql
```

This creates the append-only `audit_log` table and revokes `DELETE` and `UPDATE` permissions from the application user.

### Step 4 — Start the backend API

```bash
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API is now live at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Step 5 — Start the Transform Engine worker

In a second terminal:

```bash
cd backend
source ../.venv/bin/activate
python -m app.transform.worker
```

This is the Kafka consumer loop that picks events off the `sws-to-dept` topic, runs schema mapping, and routes writes to department adapters.

### Step 6 — Start mock department servers

In a third terminal:

```bash
python mock_departments/server.py
```

This starts three mock department APIs on ports 8001, 8002, 8003 — simulating Factories, Labour, and Fire Safety.

### Step 7 — Start the frontend

In a fourth terminal:

```bash
cd frontend
npm run dev
```

Frontend is now live at `http://localhost:3000`.

---

## Core flows

### Flow 1 — SWS address change propagates to all departments

```
POST /webhook/sws-event
{
  "ubid": "KA-BLR-2024-001234",
  "event_type": "address_update",
  "owner_name": "Ravi Kumar",
  "new_address": "42 MG Road, Bengaluru 560001",
  "gstin": "29ABCDE1234F1Z5"
}

→ Idempotency key checked in Redis
→ PII scrubber tokenizes GSTIN and address
→ Event queued on Kafka: sws-to-dept
→ Transform Engine maps to Factories schema: { proprietor, premise_address }
→ Transform Engine maps to Labour schema: { applicant_full_name, registered_address }
→ Both writes dispatched to mock dept APIs
→ Audit store records: UBID, source, destination, payload hash, outcome, timestamp
```

Expected result: all three department endpoints receive the mapped payload within 5 seconds. Audit log shows three entries with `outcome: success`.

### Flow 2 — Department update reaches SWS

```
Factories system changes a signatory field (detected via Tier 2 polling)

→ Ingestion engine detects delta on next poll cycle
→ Normalised and placed on Kafka: dept-to-sws
→ Transform Engine maps Factories schema → SWS schema
→ UBID join resolves the business identity
→ SWS API updated with the new value
→ Audit store records the full chain
```

### Flow 3 — Conflict detected and resolved

Trigger a conflict by sending two updates for the same UBID within 60 seconds:

```bash
# Terminal 1
curl -X POST http://localhost:8000/webhook/sws-event \
  -H "Content-Type: application/json" \
  -d '{"ubid": "KA-BLR-2024-001234", "event_type": "address_update", "new_address": "42 MG Road"}'

# Terminal 2 (within 60 seconds)
curl -X POST http://localhost:8000/webhook/dept-event \
  -H "Content-Type: application/json" \
  -d '{"ubid": "KA-BLR-2024-001234", "event_type": "address_update", "new_address": "17 Residency Road"}'
```

The Conflict Resolver holds both updates. The frontend Conflict Review page shows a card with both values. The default policy (`SWS-wins`) applies automatically — or a human selects the correct value for sensitive fields (PAN, GSTIN, signatory). The audit store records which source won, which was discarded, the policy applied, and when.

### Flow 4 — New department onboarded

```bash
curl -X POST http://localhost:8000/mappings/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "department": "fire_safety",
    "fields": ["owner_nm", "biz_address", "license_no", "contact_phone"]
  }'
```

The Transform Engine computes semantic similarity scores between these fields and the SWS schema. Mappings above `0.85` confidence are auto-confirmed. Fields below the threshold appear in the Mapping Registry UI for one-time human review. Once approved, the adapter goes live — no changes to the core layer required.

---

## Configuration

All configuration is via environment variables in `.env`:

```env
# Kafka
KAFKA_BROKER=localhost:9092
KAFKA_CONSUMER_GROUP=sanchaarsetu-core

# Redis
REDIS_URL=redis://localhost:6379
IDEMPOTENCY_WINDOW_SECONDS=120

# PostgreSQL
DATABASE_URL=postgresql://setu:setu@localhost:5432/sanchaarsetu

# Transform Engine
MAPPING_CONFIDENCE_THRESHOLD=0.85
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=mps        # mps | cuda | cpu

# Conflict Resolver
CONFLICT_WINDOW_SECONDS=60
DEFAULT_CONFLICT_POLICY=sws-wins   # sws-wins | last-write-wins | manual

# Security
TLS_ENABLED=false           # set true in production
PII_TOKEN_TTL_SECONDS=300

# Department API keys (one per department)
FACTORIES_API_KEY=your-key-here
LABOUR_API_KEY=your-key-here
FIRE_SAFETY_API_KEY=your-key-here
```

---

## Security model

| Threat | Mitigation |
|--------|-----------|
| Data intercepted in transit | TLS 1.3 on all connections |
| Unauthorized updates | Mutual TLS + per-department API keys |
| PII sent to AI model | PII scrubber tokenizes before Transform Engine; real values reinserted after |
| Compromised department flooding | Per-department rate limiting; queue paused on spike |
| Audit log tampering | Append-only PostgreSQL; `DELETE` and `UPDATE` revoked; optional hash chaining |
| Cross-department data leakage | Role-based access; each department reads and writes only its own scope |
| Malformed payloads | Schema validation on every incoming payload; unexpected fields rejected |

The PII scrubber is a hard constraint — no raw personal data ever reaches the sentence transformer or any hosted model. Tokenization happens before the Kafka queue; real values are reinserted by the adapter after mapping is complete.

---

## Testing

### Unit tests

```bash
cd backend
pytest tests/unit/
```

Covers: PII scrubber tokenization and restore, idempotency key generation, conflict policy selection, schema mapping confidence thresholds.

### Integration tests

```bash
pytest tests/integration/
```

Requires the Docker stack to be running. Covers: end-to-end address change propagation, department-to-SWS sync, conflict detection and resolution, DLQ behaviour on adapter failure.

### Manual smoke test

```bash
bash scripts/smoke_test.sh
```

Fires one event per flow and prints pass/fail for each. Safe to run at any time — uses a dedicated test UBID that is excluded from the live audit log.

---

## Onboarding a new department

Adding a new department takes approximately one working day and requires no changes to the core layer.

1. **Create a thin adapter** — copy `backend/app/adapters/mock_dept.py` and implement the `read()` and `write()` methods for the new department's API.

2. **Register the adapter** — add the department entry to `backend/app/adapters/registry.py` with its UBID scope and tier assignment.

3. **Generate suggested mappings** — call `POST /mappings/suggest` with the department's field list. The Transform Engine returns confidence scores for each field against the SWS schema.

4. **Review in UI** — open the Mapping Registry page. Approve or manually correct any field below the 0.85 threshold. Confirmed mappings are stored in pgvector and reused — no repeated inference.

5. **Set environment variables** — add the department's API key and rate limit to `.env`.

6. **Run integration test** — `pytest tests/integration/test_new_department.py --dept=your_dept_name`

The department is now live.

---

## Hackathon demo guide

Four flows, four minutes. Run them in this order.

| # | Flow | What to show |
|---|------|-------------|
| 1 | Address change on SWS | Fire the webhook, watch the Dashboard — three department entries appear within 5 seconds, all green |
| 2 | Department update reaches SWS | Trigger a mock dept change, show the audit log entry with the full chain from detection to SWS write |
| 3 | Conflict resolution | Fire two concurrent updates, show the Conflict Review card, resolve manually, show audit entry with `conflict: true` and `resolution: sws-wins` |
| 4 | New department onboarding | Call `/mappings/suggest`, show the Mapping Registry UI with confidence scores, approve one field below threshold, show it go live |

The audit log is the most compelling visual — every event in plain language, hash-chained, with outcome and timestamp. Keep it visible throughout the demo.

---

## Built with

- [FastAPI](https://fastapi.tiangolo.com) — async Python API framework
- [Apache Kafka](https://kafka.apache.org) — durable message queue
- [Sentence Transformers](https://sbert.net) — semantic field name matching
- [pgvector](https://github.com/pgvector/pgvector) — vector similarity search in PostgreSQL
- [Redis](https://redis.io) — idempotency key store
- [Temporal.io](https://temporal.io) — stateful workflow orchestration
- [React](https://react.dev) + [Vite](https://vitejs.dev) + [Tailwind CSS](https://tailwindcss.com) — frontend

---

*SanchaarSetu — built for Karnataka's Single Window System interoperability challenge.*