# Smart City Orchestrator

Event orchestration system for a smart city that receives events from different services, normalizes data, applies business rules, and generates derived events for other services.

## Architecture

The system is based on an event-oriented architecture with the following main components:

### Main Components

1. **API (FastAPI)**
   - Receives events via REST endpoint `/ingest/{service}`
   - Validates and processes events through the application layer
   - Exposes endpoint for querying stored events

2. **Application Layer (`app/application/`)**
   - `ingest.py`: Orchestrates the event ingestion flow
   - Manages event deduplication
   - Persists base and derived events

3. **Domain Layer (`app/domain/`)**
   - **Event Normalization** (`events/normalization/`):
     - Normalizes received payloads using Pydantic schemas
     - Supports different payload types (Health, Energy, Transport, Security)
   - **Business Rules** (`events/rules/`):
     - Evaluates normalized events and generates derived events
     - Implements orchestration logic between services
   - **Orchestration** (`orchestration/`):
     - Registry of factories per service
     - Factories that combine normalizers and rule evaluators

4. **Infrastructure Layer (`app/infra/`)**
   - **Persistence** (`persistence/`):
     - SQLAlchemy models for Event and OutboxMessage
     - Repositories for data access
   - **Outbox Pattern** (`outbox/`):
     - Worker that processes pending messages
     - Ensures delivery of derived events to other services
     - Implements retry and attempt control

5. **Database (PostgreSQL)**
   - Stores base and derived events
   - Outbox table for asynchronous processing
   - Support for deduplication via unique key

### Processing Flow

```
1. Event received via API → /ingest/{service}
2. Factory Registry identifies the service
3. Normalizer validates and normalizes the payload
4. Rule evaluator processes the normalized event
5. Derived events are created and persisted
6. Notifications are enqueued in the outbox
7. Worker processes outbox and publishes events
```

### Architectural Patterns

- **Factory Pattern**: Each service has a factory that provides normalizer and rule evaluator
- **Strategy Pattern**: Different normalization and evaluation strategies per service
- **Outbox Pattern**: Guarantees delivery of derived events
- **Repository Pattern**: Data access abstraction

## How to Run the Project

### Prerequisites

- Docker and Docker Compose installed
- Make (optional, but recommended)

### Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd smartcity-orchestrator
```

2. Create a `.env` file in the project root with the following variables:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
```

### Running with Docker Compose

#### Complete Setup (Recommended)
```bash
make setup
```
This command will:
- Build Docker images
- Start all services
- Wait for the database to be ready
- Run database migrations

#### Individual Commands

**Build images:**
```bash
make build
```

**Start services:**
```bash
make up
```

**Start and view logs:**
```bash
make up-logs
```

**Stop services:**
```bash
make down
```

**View logs:**
```bash
make logs              # All services
make logs-api          # API only
make logs-db           # Database only
make logs-worker       # Worker only
```

**Run migrations:**
```bash
make migrate           # Apply all migrations
make migrate-status    # View current status
make migrate-history   # View migration history
```

**Run tests:**
```bash
make test              # All tests
make test-cov          # With coverage
make test-file FILE=tests/api/test_routes.py  # Specific file
```

**Open shell in container:**
```bash
make shell
```

**Clean volumes and containers:**
```bash
make clean
```

### Accessing the API

After starting the services, the API will be available at:
- **API**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Available Endpoints

- `GET /health` - Health check
- `POST /ingest/{service}` - Event ingestion
- `GET /events` - List events (with pagination)

## Examples of Payloads and Created Rules

### 1. Service: Health

#### Input Payload
```json
{
  "patient_id": 12345,
  "alert": "emergency",
  "location": "Rua das Flores, 100"
}
```

#### Normalization Schema
```python
class HealthPayload(BasePayload):
    patient_id: Optional[int] = None
    alert: Optional[str] = None
    location: Optional[str] = None
```

#### Implemented Rule
When `alert == "emergency"`, the system generates **two derived events**:

1. **Event for Transport**:
```json
{
  "action": "dispatch_nearest_vehicle",
  "reason": "health_emergency",
  "location": "Rua das Flores, 100",
  "patient_id": 12345
}
```
- Deduplication Key: `health_emergency_{patient_id}`

2. **Event for Security**:
```json
{
  "priority": "high",
  "action": "escort_and_clear_traffic",
  "reason": "health_emergency",
  "location": "Rua das Flores, 100",
  "patient_id": 12345
}
```
- Deduplication Key: `health_emergency_{patient_id}`

#### Example Request
```bash
curl -X POST "http://localhost:8000/ingest/health" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 12345,
    "alert": "emergency",
    "location": "Rua das Flores, 100"
  }'
```

#### Response
```json
{
  "stored_event_id": "550e8400-e29b-41d4-a716-446655440000",
  "derived_events": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

---

### 2. Service: Energy

#### Input Payload
```json
{
  "energy": 650.0,
  "neighborhood": "downtown"
}
```

#### Normalization Schema
```python
class EnergyPayload(BasePayload):
    energy: Optional[float] = None
    neighborhood: Optional[str] = None
```

#### Implemented Rule
When `energy > 500.0 kWh`, the system generates an event for Security:

**Event for Security**:
```json
{
  "alert": "possible_risk",
  "reason": "critical_energy_usage",
  "neighborhood": "downtown",
  "energy": 650.0
}
```
- Deduplication Key: `critical_energy_usage_{neighborhood}`
- Configurable threshold: `THRESHOLD_KWH = 500.0`

#### Example Request
```bash
curl -X POST "http://localhost:8000/ingest/energy" \
  -H "Content-Type: application/json" \
  -d '{
    "energy": 650.0,
    "neighborhood": "downtown"
  }'
```

#### Case with No Derived Events
If `energy <= 500.0`, no derived events are generated:
```bash
curl -X POST "http://localhost:8000/ingest/energy" \
  -H "Content-Type: application/json" \
  -d '{
    "energy": 400.0,
    "neighborhood": "suburbs"
  }'
```

Response:
```json
{
  "stored_event_id": "550e8400-e29b-41d4-a716-446655440003",
  "derived_events": []
}
```

---

### 3. Service: Transport

#### Input Payload
```json
{
  "bus_id": 42,
  "lat": -23.5505,
  "lon": -46.6333
}
```

#### Normalization Schema
```python
class TransportPayload(BasePayload):
    bus_id: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
```

#### Behavior
This service currently does not have rules that generate derived events. Events are only normalized and stored.

#### Example Request
```bash
curl -X POST "http://localhost:8000/ingest/transport" \
  -H "Content-Type: application/json" \
  -d '{
    "bus_id": 42,
    "lat": -23.5505,
    "lon": -46.6333
  }'
```

---

### 4. Service: Security

#### Input Payload
```json
{
  "alert": true,
  "camera_trigger": "motion_detected"
}
```

#### Normalization Schema
```python
class SecurityPayload(BasePayload):
    alert: Optional[bool] = None
    camera_trigger: Optional[str] = None
```

#### Behavior
This service currently does not have rules that generate derived events. Events are only normalized and stored.

#### Example Request
```bash
curl -X POST "http://localhost:8000/ingest/security" \
  -H "Content-Type: application/json" \
  -d '{
    "alert": true,
    "camera_trigger": "motion_detected"
  }'
```

---

### 5. Event Deduplication

The system supports deduplication through the `dedupe_key` parameter:

```bash
curl -X POST "http://localhost:8000/ingest/energy?dedupe_key=unique_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "energy": 600.0,
    "neighborhood": "downtown"
  }'
```

If the same `dedupe_key` is used again, the system returns the existing event without creating duplicates.

---

### 6. Querying Events

To list stored events:

```bash
curl "http://localhost:8000/events?limit=10&offset=0"
```

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "service": "health",
    "timestamp": "2024-01-15T10:30:00Z",
    "payload": {
      "patient_id": 12345,
      "alert": "emergency",
      "location": "Rua das Flores, 100"
    },
    "normalized_payload": {
      "patient_id": 12345,
      "alert": "emergency",
      "location": "Rua das Flores, 100"
    },
    "deduplication_key": null,
    "source_event_id": null,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "service": "transport",
    "timestamp": "2024-01-15T10:30:00Z",
    "payload": {
      "action": "dispatch_nearest_vehicle",
      "reason": "health_emergency",
      "location": "Rua das Flores, 100",
      "patient_id": 12345
    },
    "normalized_payload": null,
    "deduplication_key": "health_emergency_12345",
    "source_event_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## Directory Structure

```
smartcity-orchestrator/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # REST endpoints (FastAPI)
│   ├── application/      # Application logic
│   ├── core/             # Configuration and DB connection
│   ├── domain/           # Domain logic
│   │   ├── events/       # Normalization and rules
│   │   └── orchestration/ # Factories and registry
│   ├── infra/            # Infrastructure
│   │   ├── outbox/       # Worker and enqueue
│   │   └── persistence/  # Models and repositories
│   └── main.py          # FastAPI application
├── tests/                # Unit and integration tests
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Docker image
├── Makefile              # Helper commands
└── requirements.txt      # Python dependencies
```

## Technologies Used

- **FastAPI**: Web framework for REST API
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM for Python
- **Alembic**: Database migrations
- **Pydantic**: Data validation and schemas
- **Docker & Docker Compose**: Containerization
- **pytest**: Testing framework

## Development

### Creating a New Migration

```bash
make migrate-create MESSAGE="migration description"
```

### Running Tests

```bash
make test              # All tests
make test-cov          # With coverage report
make test-pattern PATTERN="test_ingest"  # Specific tests
```

### Adding a New Service

1. Create payload schema in `app/domain/events/normalization/payloads.py`
2. Create normalizer (or use `PydanticEventNormalizer`)
3. Create rule evaluator in `app/domain/events/rules/`
4. Create factory in `app/domain/orchestration/factories/`
5. Register in `FactoryRegistry` in `app/domain/orchestration/registry.py`

## License

[Specify license]
