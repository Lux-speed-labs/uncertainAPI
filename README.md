# UncertainAPI

**AI-Powered Web Extraction Framework** - Extract data from any website using multi-agent AI orchestration.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2%2B-green)](https://www.djangoproject.com/)
[![Async](https://img.shields.io/badge/async-first-brightgreen)](ASYNC_ARCHITECTURE.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **⚡ Fully Async**: Built with async/await for 10-20x performance improvement on concurrent operations

## Overview

UncertainAPI is a Django/DRF framework that uses AI agents to intelligently navigate websites, handle authentication, solve captchas, and extract structured data—**no manual selectors required**. Built on [AG2 (formerly AutoGen)](https://github.com/ag2ai/ag2) for robust multi-agent orchestration.

### Key Features

- 🤖 **AI-Orchestrated Extraction**: Multi-agent system handles the entire extraction workflow
- 🔐 **Smart Authentication**: Automatic login, OAuth, token, and session management
- 🧩 **Zero Configuration**: Works without explicit selectors or DOM knowledge
- 🔄 **Pagination Support**: Automatically detects and navigates through pages
- 📦 **Pydantic Schemas**: Define data structure, AI handles extraction
- ⚡ **Background Tasks**: Schedule extraction with Celery, Django-Q, or custom backends
- 🔌 **Pluggable**: Swap browser backends (Playwright, Selenium, httpx), AI providers (OpenAI, Anthropic, local models)
- 🎯 **DRF Integration**: Extractors as async API endpoints with caching and serialization
- ⚡ **Async-First**: All I/O operations use async/await for maximum performance
- 📝 **Loguru Logging**: Beautiful, structured logging with automatic context

## Installation

```bash
# Basic installation
pip install uncertainapi

# With specific backends
pip install uncertainapi[playwright]      # Playwright (recommended)
pip install uncertainapi[selenium]        # Selenium
pip install uncertainapi[requests]        # Lightweight requests+BeautifulSoup

# With AI providers
pip install uncertainapi[openai]          # OpenAI
pip install uncertainapi[anthropic]       # Anthropic Claude
pip install uncertainapi[litellm]         # LiteLLM (Ollama, local models)

# With task schedulers
pip install uncertainapi[celery]          # Celery
pip install uncertainapi[django-q]        # Django-Q

# Full installation (all extras)
pip install uncertainapi[full]
```

## Quick Start

### 1. Create a New Project

```bash
uncertainapi createproject myproject
cd myproject
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `myproject/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'uncertainAPI',
    'myapp',  # Your extractor app
]

UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': 'uncertainAPI.ai.providers.openai.OpenAIProvider',
        'API_KEY': 'your-openai-api-key',
        'MODEL': 'gpt-4o',
    },
    'BROWSER_BACKEND': {
        'BACKEND': 'uncertainAPI.browsers.playwright.PlaywrightBackend',
        'HEADLESS': True,
        'TIMEOUT': 30000,
    },
}
```

### 3. Define Your Schema

Create `myapp/schemas.py`:

```python
from uncertainAPI.schemas import ExtractionSchema
from typing import Optional

class ProductSchema(ExtractionSchema):
    """Product data schema."""
    
    name: str
    price: float
    description: str
    in_stock: bool
    rating: Optional[float] = None
    image_url: Optional[str] = None
```

### 4. Create an Extractor View

Create `myapp/views.py`:

```python
from uncertainAPI.views import ExtractorView
from .schemas import ProductSchema

class ProductScraperView(ExtractorView):
    """Extract product data from e-commerce sites."""
    
    url = "https://example.com/products"
    schema_class = ProductSchema
    enable_caching = True
    cache_ttl = 3600
    pagination = True  # Automatically handle pagination
```

### 5. Add URL Pattern

In `myapp/urls.py`:

```python
from django.urls import path
from .views import ProductScraperView

urlpatterns = [
    path('extract/products/', ProductScraperView.as_view(), name='extract-products'),
]
```

### 6. Run and Test

```bash
python manage.py migrate

# Use ASGI server (required for async views)
pip install uvicorn[standard]
uvicorn myproject.asgi:application --reload
```

Visit: `http://localhost:8000/extract/products/`

> **Note**: UncertainAPI requires an **ASGI server** (Uvicorn, Daphne) for async support. Traditional WSGI servers won't work.

## Architecture

UncertainAPI uses a multi-agent architecture powered by AG2:

```
Request → ExtractorView → ExtractorOrchestrator → Multi-Agent System
                                                ├─ CoordinatorAgent (orchestrates workflow)
                                                ├─ NavigatorAgent (browser control, auth, captcha)
                                                ├─ ExtractionAgent (data extraction)
                                                ├─ ValidationAgent (quality assurance)
                                                └─ PaginationAgent (handles pagination)
                                                         ↓
                                            Structured Data → DRF Response
```

## Advanced Usage

### Custom Authentication

```python
from uncertainAPI.auth.basic import BasicAuthHandler
from uncertainAPI.views import ExtractorView

class AuthenticatedScraperView(ExtractorView):
    url = "https://members.example.com/dashboard"
    schema_class = DashboardSchema
    auth_handler_class = BasicAuthHandler
    
    def get_auth_handler(self, request):
        credentials = {
            "username": request.user.username,
            "password": request.data.get("password"),
        }
        return BasicAuthHandler(
            credentials=credentials,
            username_selector="#username",
            password_selector="#password",
            submit_selector="button[type='submit']",
        )
```

### Background Extraction

```python
class BackgroundScraperView(ExtractorView):
    url = "https://example.com/large-dataset"
    schema_class = DataSchema
    enable_background = True  # Schedule task instead of blocking
    
    def post(self, request):
        # Task scheduled, returns immediately
        return super().post(request)
```

### Persistence to Database

```python
from uncertainAPI.mixins import PersistenceMixin
from uncertainAPI.views import ExtractorView
from .models import Product

class PersistentScraperView(PersistenceMixin, ExtractorView):
    url = "https://example.com/products"
    schema_class = ProductSchema
    model_class = Product  # Auto-saves to database
```

### Custom Agent Configuration

```python
from uncertainAPI.agents.orchestrator import ExtractorOrchestrator
from uncertainAPI.agents.roles import NavigatorAgent, ExtractionAgent

class CustomScraperView(ExtractorView):
    def get_orchestrator(self, url, request):
        orchestrator = super().get_orchestrator(url, request)
        
        # Add custom agents
        custom_agents = [
            MyCustomAgent(name="custom"),
            *orchestrator.get_agents(),
        ]
        orchestrator.agents = custom_agents
        
        return orchestrator
```

### Multiple Browser Backends

```python
# In settings.py - switch to Selenium
UNCERTAINAPI = {
    'BROWSER_BACKEND': {
        'BACKEND': 'uncertainAPI.browsers.selenium.SeleniumBackend',
        'BROWSER_TYPE': 'chrome',
        'HEADLESS': True,
    },
}

# Or use lightweight requests for static pages
UNCERTAINAPI = {
    'BROWSER_BACKEND': {
        'BACKEND': 'uncertainAPI.browsers.requests.RequestsBackend',
        'TIMEOUT': 30,
    },
}
```

### AI Provider Options

```python
# OpenAI (default)
UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': 'uncertainAPI.ai.providers.openai.OpenAIProvider',
        'API_KEY': 'sk-...',
        'MODEL': 'gpt-4o',
    },
}

# Anthropic Claude
UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': 'uncertainAPI.ai.providers.anthropic.AnthropicProvider',
        'API_KEY': 'sk-ant-...',
        'MODEL': 'claude-3-5-sonnet-20241022',
    },
}

# Local models via Ollama
UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': 'uncertainAPI.ai.providers.litellm.LiteLLMProvider',
        'MODEL': 'ollama/llama2',
        'API_BASE': 'http://localhost:11434',
    },
}
```

## Configuration Reference

### Settings Structure

```python
UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': str,              # AI provider class path
        'API_KEY': str,              # API key
        'MODEL': str,                # Model name
        'BASE_URL': str,             # Optional: custom API base URL
    },
    'BROWSER_BACKEND': {
        'BACKEND': str,              # Browser backend class path
        'HEADLESS': bool,            # Run headless
        'TIMEOUT': int,              # Timeout in milliseconds
        'BROWSER_TYPE': str,         # Browser type (for Selenium)
    },
    'ORCHESTRATOR': {
        'BACKEND': str,              # Custom orchestrator class
        'MAX_ROUNDS': int,           # Max agent conversation rounds
        'PATTERN': str,              # Orchestration pattern ('auto', 'sequential')
        'ENABLE_HUMAN_VALIDATION': bool,  # Human-in-the-loop
    },
    'TASK_SCHEDULER': {
        'BACKEND': str,              # Task scheduler class path
    },
    'CACHE_BACKEND': str,            # Django cache alias
    'DEFAULT_AUTH_STORAGE': str,     # 'database', 'cache', or 'memory'
}
```

## CLI Commands

```bash
# Create new project
uncertainapi createproject myproject

# Create new extractor app
uncertainapi startapp myapp
```

## Testing

```bash
# Install dev dependencies
pip install uncertainapi[dev]

# Run tests
pytest

# With coverage
pytest --cov=uncertainAPI --cov-report=term-missing
```

## Project Structure

```
myproject/
├── manage.py
├── requirements.txt
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── __init__.py
    ├── apps.py
    ├── schemas.py      # Pydantic extraction schemas
    ├── views.py        # Extractor views
    ├── models.py       # Optional: persistence models
    └── urls.py
```

## How It Works

1. **Request**: User hits extractor endpoint
2. **Coordination**: CoordinatorAgent plans the extraction workflow
3. **Navigation**: NavigatorAgent uses browser tools to fetch the page
4. **Authentication**: If needed, handles login/OAuth/captcha automatically
5. **Extraction**: ExtractionAgent analyzes HTML and extracts data matching schema
6. **Validation**: ValidationAgent checks data quality and completeness
7. **Pagination**: If enabled, PaginationAgent detects and navigates additional pages
8. **Response**: Validated data returned as JSON via DRF

All agent interactions are orchestrated by AG2 for robust, adaptive behavior.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built on [AG2](https://github.com/ag2ai/ag2) for multi-agent orchestration
- Inspired by the need for intelligent, adaptable web extraction
- Designed with SOLID principles and extensibility in mind

## Documentation

📚 **[Complete Documentation Index](DOCUMENTATION_INDEX.md)** - All guides organized by topic

**Quick Links**:
- [🚀 Installation Guide](INSTALL.md) - Install locally (pre-PyPI)
- [📖 Getting Started](GETTING_STARTED_LOCAL.md) - Complete walkthrough
- [⚡ Quick Reference](QUICK_REFERENCE.md) - One-page cheat sheet
- [🎯 Quick Start](QUICKSTART.md) - 5-minute tutorial
- [⚙️ Async Architecture](ASYNC_ARCHITECTURE.md) - Async patterns
- [🌐 Deployment](DEPLOYMENT.md) - Production setup

## Support

- **Issues**: [GitHub Issues](https://github.com/Lux-speed-labs/uncertainAPI/issues)
- **Examples**: See `/examples` directory

---

**UncertainAPI** - Because web extraction shouldn't require certainty about the DOM structure.
