# UncertainAPI

A comprehensive AI-native Django REST framework designed for building solutions that depend on uncertain and unconventional third-party integrations. UncertainAPI provides a robust foundation for handling asynchronous operations, web scraping, AI agent workflows, and real-time progress tracking.

## Features

### Core Capabilities
- **Django 4.2 + DRF**: Modern REST API framework with comprehensive OpenAPI documentation
- **Auto Sync→Async Handoff**: Immediate response with background job execution and ETA tracking
- **Celery + Redis**: Distributed task queue for background job processing
- **Django Channels**: WebSocket/SSE support for real-time progress updates
- **PostgreSQL**: Production-ready database with proper indexing
- **Idempotency Middleware**: Safe request retry mechanism with automatic deduplication

### Advanced Features
- **Playwright Web Scraping**: Headless browser automation with JavaScript support
- **Pluggable Connectors**: Extensible framework for third-party integrations
- **LangGraph Agent Stubs**: AI workflow automation framework
- **MCP Server**: Model Context Protocol server for AI model communication
- **Real-time Progress**: WebSocket connections for live job status updates
- **Comprehensive Testing**: pytest-based test suite with async support

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd uncertainAPI
   cp .env.example .env
   ```

2. **Start services**:
   ```bash
   make docker-up
   ```

3. **Access the API**:
   - API Root: http://localhost:8000/api/v1/
   - API Documentation: http://localhost:8000/api/docs/
   - Admin Interface: http://localhost:8000/admin/

### Local Development

1. **Install dependencies**:
   ```bash
   make install
   ```

2. **Setup database**:
   ```bash
   make migrate
   make superuser
   ```

3. **Run development servers**:
   ```bash
   # Terminal 1: Django server
   make run
   
   # Terminal 2: Celery worker
   make celery
   
   # Terminal 3: Celery beat (optional)
   make celery-beat
   ```

## API Endpoints

### Core Endpoints

- `GET /api/v1/` - API root with available endpoints
- `GET /api/v1/health/` - Health check endpoint
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation

### Job Management

- `POST /api/v1/jobs/` - Create a new background job
- `GET /api/v1/jobs/` - List all jobs (filtered by user)
- `GET /api/v1/jobs/{id}/` - Get job details with progress
- `POST /api/v1/jobs/{id}/cancel/` - Cancel a running job

### Web Scraping

- `POST /api/v1/scrape/` - Start web scraping job

**Example Request**:
```json
{
  "url": "https://example.com",
  "wait_time": 5,
  "extract_links": true,
  "extract_text": true,
  "css_selectors": [".content", ".title"]
}
```

**Response**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "estimated_completion": "2024-01-01T12:05:00Z",
  "websocket_url": "/ws/jobs/123e4567-e89b-12d3-a456-426614174000/progress/"
}
```

### Real-time Progress

Connect to WebSocket endpoint for live updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}/progress/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Progress:', data.progress + '%');
    console.log('Current step:', data.current_step);
};
```

## Architecture

### Sync→Async Pattern

UncertainAPI implements a sophisticated sync→async handoff pattern:

1. **Immediate Response**: API endpoints return immediately with job ID
2. **Background Processing**: Tasks execute asynchronously via Celery
3. **Progress Tracking**: Real-time updates via WebSocket/polling
4. **ETA Calculation**: Dynamic completion time estimates

### Job Lifecycle

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   pending   │───▶│   started    │───▶│  progress   │───▶│   success    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
      │                     │                                      ▲
      │                     │            ┌─────────────┐          │
      │                     └───────────▶│   failure   │──────────┘
      │                                  └─────────────┘
      │            ┌─────────────┐
      └───────────▶│   revoked   │
                   └─────────────┘
```

### Components

- **Apps Structure**:
  - `core/` - Base functionality, health checks, middleware
  - `jobs/` - Background job management and WebSocket consumers
  - `scraping/` - Playwright-based web scraping
  - `connectors/` - Pluggable third-party integrations
  - `agents/` - LangGraph AI agent workflows
  - `mcp/` - Model Context Protocol server

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DB_NAME=uncertainapi
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/1

# Security
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Development Settings

The project includes comprehensive settings for:
- Database connection pooling
- Celery task configuration
- Channel layers for WebSockets
- Logging with file and console handlers
- CORS configuration
- OpenAPI documentation

## Testing

Run the test suite:

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=apps

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run only integration tests
```

### Test Structure

- Unit tests for models, serializers, views
- Integration tests for API endpoints
- WebSocket connection tests
- Celery task execution tests

## Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking (if using mypy)
mypy apps/
```

### Adding New Connectors

1. Create connector class inheriting from `BaseConnectorTool`
2. Implement `execute()` and `get_schema()` methods
3. Add to connector registry
4. Create corresponding serializers and viewsets

Example:
```python
class CustomAPIConnector(BaseConnectorTool):
    def execute(self, endpoint, **kwargs):
        # Implementation here
        pass
    
    def get_schema(self):
        return {
            'input': {'endpoint': {'type': 'string'}},
            'output': {'data': {'type': 'object'}}
        }
```

### Adding New Agent Types

1. Inherit from `BaseAgent` in `apps/agents/langgraph_agents.py`
2. Implement `execute()` and `get_capabilities()` methods
3. Add to `AVAILABLE_AGENTS` registry

## Deployment

### Docker Production

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup

1. Set up PostgreSQL database
2. Configure Redis instance
3. Set environment variables
4. Run migrations
5. Collect static files
6. Start Celery workers

## Monitoring

### Health Checks

- Application: `GET /api/v1/health/`
- Database: Automatic via Django ORM
- Redis: Celery worker status
- Job Queue: Monitor via Celery Flower

### Logging

Logs are configured for:
- Application events: `/logs/uncertainapi.log`
- Celery tasks: Console and file
- Django framework: Configurable log level

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Write tests for new functionality
4. Ensure all tests pass: `make test`
5. Format code: `make format`
6. Submit pull request

## License

[License information here]

## Support

For questions and support:
- GitHub Issues: [Repository issues]
- Documentation: [Additional docs]
- Community: [Discord/Slack links]
