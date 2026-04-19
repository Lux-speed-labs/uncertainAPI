# UncertainAPI Quick Reference

A one-page cheat sheet for common tasks.

## Installation

```bash
# Local development install
cd /path/to/uncertainAPI
pip install -e ".[full]"
```

## CLI Commands

```bash
# Create project
uncertainapi createproject myproject

# Create app
uncertainapi startapp myapp

# Check version
uncertainapi --version
```

## Project Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py      # Configure here
│   ├── urls.py
│   ├── asgi.py         # ASGI config (required)
│   └── wsgi.py
└── myapp/
    ├── schemas.py      # Define extraction schemas
    ├── views.py        # Define extractors
    ├── models.py       # Optional: persistence
    └── urls.py         # URL routing
```

## Basic Extractor

```python
# schemas.py
from uncertainAPI.schemas import ExtractionSchema

class ProductSchema(ExtractionSchema):
    name: str
    price: float
    in_stock: bool

# views.py
from uncertainAPI.views import ExtractorView
from .schemas import ProductSchema

class ProductExtractorView(ExtractorView):
    url = "https://example.com/products"
    schema_class = ProductSchema
```

## Configuration (settings.py)

```python
UNCERTAIN_API = {
    # Required
    'BROWSER_BACKEND': 'playwright',  # or 'selenium', 'requests'
    'AI_PROVIDER': 'openai',          # or 'anthropic', 'litellm'
    'OPENAI_API_KEY': 'sk-...',
    
    # Optional
    'PLAYWRIGHT_CONFIG': {
        'HEADLESS': True,
        'TIMEOUT': 30000,
    },
    'TASK_BACKEND': 'celery',  # for background tasks
    'LOGURU_LEVEL': 'INFO',
}
```

## Running

```bash
# MUST use ASGI server (not manage.py runserver)
uvicorn myproject.asgi:application --reload

# Or with Daphne
daphne myproject.asgi:application
```

## Common Patterns

### Dynamic URL

```python
class DynamicExtractorView(ExtractorView):
    schema_class = MySchema
    # No fixed URL - pass via query param
    # GET /extract/?url=https://example.com
```

### With Authentication

```python
from uncertainAPI.auth.basic import BasicAuthHandler

class AuthExtractorView(ExtractorView):
    url = "https://example.com"
    schema_class = MySchema
    auth_handler_class = BasicAuthHandler
    auth_config = {
        'username': 'user',
        'password': 'pass',
        'login_url': 'https://example.com/login',
    }
```

### With Pagination

```python
class PaginatedExtractorView(ExtractorView):
    url = "https://example.com/products"
    schema_class = ProductSchema
    pagination = True
    max_pages = 10
```

### With Caching

```python
class CachedExtractorView(ExtractorView):
    url = "https://example.com/data"
    schema_class = DataSchema
    enable_caching = True
    cache_ttl = 3600  # 1 hour
```

### With Persistence

```python
from uncertainAPI.mixins import PersistenceMixin
from .models import Product

class PersistentExtractorView(PersistenceMixin, ExtractorView):
    url = "https://example.com/products"
    schema_class = ProductSchema
    model_class = Product
```

### Background Tasks

```python
class BackgroundExtractorView(ExtractorView):
    url = "https://example.com/data"
    schema_class = DataSchema
    schedule_background = True
    schedule_interval = 3600  # seconds
```

## Custom Agents

```python
from uncertainAPI.agents.base import BaseExtractorAgent

class CustomAgent(BaseExtractorAgent):
    def get_name(self) -> str:
        return "CustomAgent"
    
    def get_system_message(self) -> str:
        return "You are a specialized extraction agent..."
    
    def get_tools(self) -> list:
        return [self.custom_tool]

# Use in view
class CustomExtractorView(ExtractorView):
    schema_class = MySchema
    custom_agents = [CustomAgent()]
```

## URL Routing

```python
# urls.py
from django.urls import path
from .views import ProductExtractorView

urlpatterns = [
    path('extract/', ProductExtractorView.as_view()),
]
```

## API Usage

```bash
# GET request
curl http://localhost:8000/api/extract/

# With dynamic URL
curl "http://localhost:8000/api/extract/?url=https://example.com"

# POST request
curl -X POST http://localhost:8000/api/extract/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DJANGO_SECRET_KEY=...
DEBUG=True
BROWSER_BACKEND=playwright
```

## Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing

```python
import pytest

@pytest.mark.asyncio
async def test_extractor():
    view = ProductExtractorView()
    data = await view.extract_data(url, request)
    assert len(data) > 0
```

## Logging

```python
from loguru import logger

logger.info("Starting extraction", url=url)
logger.error("Extraction failed", error=str(e))
logger.debug("Agent response", response=response)
```

## Browser Backends

| Backend | Use Case | Async | Install |
|---------|----------|-------|---------|
| Playwright | Full JS, recommended | ✅ | `pip install playwright` |
| Selenium | Alternative browser | ✅ | `pip install selenium` |
| httpx | Static pages only | ✅ | `pip install httpx` |

## AI Providers

| Provider | Use Case | Install |
|----------|----------|---------|
| OpenAI | GPT-4, GPT-3.5 | `pip install openai` |
| Anthropic | Claude | `pip install anthropic` |
| LiteLLM | 100+ providers | `pip install litellm` |

## Task Queues

| Backend | Use Case | Install |
|---------|----------|---------|
| Celery | Production | `pip install celery redis` |
| Django-Q | Simple | `pip install django-q` |
| Django Background | DB-backed | `pip install django-background-tasks` |

## Troubleshooting

```bash
# Command not found
pip install -e .

# Import errors
pip install -e ".[full]"

# Browser not found
playwright install chromium

# Async not working
# Use uvicorn, not manage.py runserver
```

## Resources

- [INSTALL.md](INSTALL.md) - Installation guide
- [GETTING_STARTED_LOCAL.md](GETTING_STARTED_LOCAL.md) - Complete walkthrough
- [QUICKSTART.md](QUICKSTART.md) - 5-minute guide
- [ASYNC_ARCHITECTURE.md](ASYNC_ARCHITECTURE.md) - Async patterns
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

## Support

- **Docs**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Issues**: [GitHub Issues](https://github.com/Lux-speed-labs/uncertainAPI/issues)
- **Examples**: See `examples/` directory

---

**UncertainAPI** - AI-powered web extraction made simple! 🚀



