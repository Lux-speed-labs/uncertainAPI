# UncertainAPI - Quick Start Guide

Get up and running with UncertainAPI in 5 minutes.

## Installation

```bash
# Install with all features
pip install uncertainapi[full]

# Or install only what you need
pip install uncertainapi[playwright,openai]
```

## Step 1: Create Project

```bash
uncertainapi createproject myproject
cd myproject
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure Settings

Edit `myproject/settings.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'uncertainAPI',
]

# Add UncertainAPI configuration
UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': 'uncertainAPI.ai.providers.openai.OpenAIProvider',
        'API_KEY': 'your-openai-api-key-here',  # Or use os.getenv('OPENAI_API_KEY')
        'MODEL': 'gpt-4o',
    },
    'BROWSER_BACKEND': {
        'BACKEND': 'uncertainAPI.browsers.playwright.PlaywrightBackend',
        'HEADLESS': True,
        'TIMEOUT': 30000,
    },
}
```

## Step 3: Create Extractor App

```bash
uncertainapi startapp products
```

Add `'products'` to `INSTALLED_APPS` in settings.py.

## Step 4: Define Schema

Edit `products/schemas.py`:

```python
from uncertainAPI.schemas import ExtractionSchema
from typing import Optional

class ProductSchema(ExtractionSchema):
    """Product data structure."""
    
    name: str
    price: float
    description: Optional[str] = None
    in_stock: bool = True
```

## Step 5: Create View

Edit `products/views.py`:

```python
from uncertainAPI.views import ExtractorView
from .schemas import ProductSchema

class ProductScraperView(ExtractorView):
    """Extract product data."""
    
    schema_class = ProductSchema
    enable_caching = True
    cache_ttl = 3600
```

## Step 6: Add URL

Create `products/urls.py`:

```python
from django.urls import path
from .views import ProductScraperView

urlpatterns = [
    path('extract/', ProductScraperView.as_view(), name='extract-products'),
]
```

Include in `myproject/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('products.urls')),
]
```

## Step 7: Run Migrations

```bash
python manage.py migrate
```

## Step 8: Start Server

```bash
python manage.py runserver
```

## Step 9: Test It

```bash
# Extract from a URL
curl "http://localhost:8000/api/products/extract/?url=https://example.com/product/123"

# Response will be:
# [
#   {
#     "name": "Product Name",
#     "price": 29.99,
#     "description": "Product description",
#     "in_stock": true
#   }
# ]
```

## Next Steps

### Add Authentication

```python
from uncertainAPI.auth.basic import BasicAuthHandler

class AuthenticatedScraperView(ExtractorView):
    schema_class = ProductSchema
    auth_handler_class = BasicAuthHandler
    
    def get_auth_handler(self, request):
        return BasicAuthHandler(
            credentials={
                'username': 'user',
                'password': 'pass',
            },
            username_selector='#username',
            password_selector='#password',
        )
```

### Enable Pagination

```python
class PaginatedScraperView(ExtractorView):
    schema_class = ProductSchema
    pagination = True  # Automatically handles multiple pages
```

### Add Background Processing

```python
class BackgroundScraperView(ExtractorView):
    schema_class = ProductSchema
    enable_background = True  # Returns task ID immediately
```

### Save to Database

```python
from uncertainAPI.mixins import PersistenceMixin
from .models import Product

class PersistentScraperView(PersistenceMixin, ExtractorView):
    schema_class = ProductSchema
    model_class = Product  # Auto-saves to database
```

### Switch Browser Backend

```python
# In settings.py
UNCERTAINAPI = {
    'BROWSER_BACKEND': {
        'BACKEND': 'uncertainAPI.browsers.selenium.SeleniumBackend',
        'BROWSER_TYPE': 'chrome',
        'HEADLESS': True,
    },
}
```

### Use Local AI Model

```python
# In settings.py
UNCERTAINAPI = {
    'AI_PROVIDER': {
        'BACKEND': 'uncertainAPI.ai.providers.litellm.LiteLLMProvider',
        'MODEL': 'ollama/llama2',
        'API_BASE': 'http://localhost:11434',
    },
}
```

## Troubleshooting

### "AG2 not installed"
```bash
pip install ag2
```

### "Playwright not installed"
```bash
pip install uncertainapi[playwright]
playwright install  # Install browsers
```

### "OpenAI API error"
- Check your API key is set correctly
- Ensure you have credits/quota

### Extraction Returns Empty Data
- The URL may require authentication
- The site may be blocking automated access
- Try with a simpler static page first

## Common Patterns

### Dynamic URL from Request
```python
class DynamicScraperView(ExtractorView):
    schema_class = ProductSchema
    
    def get_url(self, request):
        return request.query_params.get('url')
```

### Custom Agents
```python
from uncertainAPI.agents.orchestrator import ExtractorOrchestrator

class CustomScraperView(ExtractorView):
    orchestrator_class = MyCustomOrchestrator
```

### Rate Limiting
```python
from uncertainAPI.mixins import RateLimitMixin

class RateLimitedScraperView(RateLimitMixin, ExtractorView):
    rate_limit = "10/hour"
    schema_class = ProductSchema
```

## Resources

- **Full Documentation**: See README.md
- **Examples**: See `/examples` directory
- **Contributing**: See CONTRIBUTING.md
- **Issues**: [GitHub Issues](https://github.com/Lux-speed-labs/uncertainAPI/issues)

## Support

Need help? Open an issue on GitHub or check the documentation.

---

**Happy Extraction! 🚀**

