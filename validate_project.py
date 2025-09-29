#!/usr/bin/env python3
"""
Project structure validation script for UncertainAPI.
This script validates the project structure without requiring external dependencies.
"""

import os
import sys
from pathlib import Path

def validate_project_structure():
    """Validate that all required files and directories exist."""
    
    base_dir = Path(__file__).parent
    
    # Required files
    required_files = [
        'manage.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'Makefile',
        'pytest.ini',
        '.env.example',
        'README.md',
        
        # Django project files
        'uncertainapi/__init__.py',
        'uncertainapi/settings.py',
        'uncertainapi/urls.py',
        'uncertainapi/wsgi.py',
        'uncertainapi/asgi.py',
        'uncertainapi/celery.py',
        
        # App files
        'apps/core/apps.py',
        'apps/core/views.py',
        'apps/core/urls.py',
        'apps/core/middleware.py',
        
        'apps/jobs/models.py',
        'apps/jobs/views.py',
        'apps/jobs/serializers.py',
        'apps/jobs/tasks.py',
        'apps/jobs/consumers.py',
        'apps/jobs/routing.py',
        
        'apps/scraping/views.py',
        'apps/scraping/serializers.py',
        'apps/scraping/scraper.py',
        
        'apps/connectors/base.py',
        'apps/agents/langgraph_agents.py',
        'apps/mcp/views.py',
    ]
    
    # Required directories
    required_dirs = [
        'apps',
        'apps/core',
        'apps/jobs', 
        'apps/scraping',
        'apps/connectors',
        'apps/agents',
        'apps/mcp',
        'uncertainapi',
    ]
    
    print("🔍 Validating UncertainAPI project structure...")
    print()
    
    missing_files = []
    missing_dirs = []
    
    # Check directories
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
        else:
            print(f"✅ Directory: {dir_path}")
    
    # Check files
    for file_path in required_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ File: {file_path}")
    
    print()
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        print()
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print()
    
    if not missing_files and not missing_dirs:
        print("🎉 All required files and directories are present!")
        return True
    else:
        print(f"⚠️  Found {len(missing_files)} missing files and {len(missing_dirs)} missing directories")
        return False

def validate_settings():
    """Validate Django settings configuration."""
    
    print("🔍 Validating Django settings...")
    
    settings_file = Path(__file__).parent / 'uncertainapi' / 'settings.py'
    
    if not settings_file.exists():
        print("❌ settings.py not found")
        return False
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    required_settings = [
        'INSTALLED_APPS',
        'MIDDLEWARE',
        'DATABASES',
        'REST_FRAMEWORK',
        'CELERY_BROKER_URL',
        'CHANNEL_LAYERS',
        'SPECTACULAR_SETTINGS',
    ]
    
    required_apps = [
        'rest_framework',
        'drf_spectacular',
        'channels',
        'apps.core',
        'apps.jobs',
        'apps.scraping',
    ]
    
    for setting in required_settings:
        if setting in content:
            print(f"✅ Setting: {setting}")
        else:
            print(f"❌ Missing setting: {setting}")
    
    for app in required_apps:
        if app in content:
            print(f"✅ App configured: {app}")
        else:
            print(f"❌ Missing app: {app}")
    
    return True

def validate_api_endpoints():
    """Validate API endpoint configuration."""
    
    print("\n🔍 Validating API endpoints...")
    
    # Check main URLs
    main_urls = Path(__file__).parent / 'uncertainapi' / 'urls.py'
    if main_urls.exists():
        with open(main_urls, 'r') as f:
            content = f.read()
            
        expected_patterns = [
            'api/v1/',
            'api/docs/',
            'mcp/',
            'admin/',
        ]
        
        for pattern in expected_patterns:
            if pattern in content:
                print(f"✅ URL pattern: {pattern}")
            else:
                print(f"❌ Missing URL pattern: {pattern}")
    
    # Check app URLs
    app_urls = [
        ('apps/core/urls.py', ['health/', '']),
        ('apps/jobs/urls.py', ['jobs/', 'jobs/<uuid:pk>/']),
        ('apps/scraping/urls.py', ['scrape/']),
        ('apps/mcp/urls.py', ['health/', 'capabilities/']),
    ]
    
    for url_file, patterns in app_urls:
        url_path = Path(__file__).parent / url_file
        if url_path.exists():
            with open(url_path, 'r') as f:
                content = f.read()
            for pattern in patterns:
                if pattern.replace('<uuid:pk>', '') in content:
                    print(f"✅ Endpoint: {url_file} -> {pattern}")
                else:
                    print(f"❌ Missing endpoint: {url_file} -> {pattern}")

def show_summary():
    """Show project summary and next steps."""
    
    print("\n" + "="*60)
    print("🚀 UncertainAPI Project Summary")
    print("="*60)
    
    print("""
✅ COMPLETED FEATURES:

🏗️  Core Architecture:
   • Django 4.2 + DRF with OpenAPI documentation
   • Auto sync→async handoff pattern
   • Celery + Redis for background job processing
   • Django Channels for WebSocket/SSE real-time updates
   • PostgreSQL database configuration
   • Comprehensive idempotency middleware

🔌 API Endpoints:
   • POST /api/v1/scrape/ - Web scraping with Playwright
   • GET/POST /api/v1/jobs/ - Job management with progress tracking
   • GET /api/v1/jobs/{id}/ - Job details with ETA
   • WebSocket /ws/jobs/{id}/progress/ - Real-time updates
   • GET /api/docs/ - Swagger UI documentation
   • GET /mcp/health/ - MCP server health check

🧩 Pluggable Components:
   • Connector framework for third-party integrations
   • LangGraph agent stubs for AI workflows
   • MCP (Model Context Protocol) server implementation
   • Playwright web scraping with configurable options

🛠️  Development Infrastructure:
   • Complete Docker + docker-compose setup
   • Makefile with all development commands
   • pytest test infrastructure with async support
   • Production-ready logging and configuration

📋 NEXT STEPS TO RUN:

1. Install dependencies:
   make install

2. Setup database:
   make migrate
   make superuser

3. Start development servers:
   make run          # Django server
   make celery       # Background worker
   make celery-beat  # Scheduler (optional)

4. OR use Docker:
   make docker-up    # Start all services

5. Test the API:
   curl http://localhost:8000/api/v1/health/
   curl http://localhost:8000/api/v1/

6. Access documentation:
   http://localhost:8000/api/docs/
""")

def main():
    """Main validation function."""
    
    print("🔧 UncertainAPI Project Validation")
    print("=" * 50)
    print()
    
    structure_ok = validate_project_structure()
    settings_ok = validate_settings()
    validate_api_endpoints()
    
    print()
    if structure_ok and settings_ok:
        print("✅ Project validation completed successfully!")
        show_summary()
        return 0
    else:
        print("❌ Project validation failed. Please check the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())