"""CLI for uncertainAPI project management."""

from __future__ import annotations

from loguru import logger
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

@click.group()
@click.version_option()
def main() -> None:
    """UncertainAPI - AI-powered web extraction framework.

    Generate Django projects configured for intelligent data extraction.
    """
    # Loguru is configured automatically
    pass

@main.command()
@click.argument("project_name")
@click.option("--dir", "-d", "target_dir", default=".", help="Target directory")
@click.option("--no-venv", is_flag=True, help="Skip virtual environment creation")
def createproject(project_name: str, target_dir: str, no_venv: bool) -> None:
    """Create a new UncertainAPI project.

    Creates a Django project pre-configured with UncertainAPI,
    DRF, and example extractor app.

    Example:
        uncertainapi createproject myproject
    """
    click.echo(f"Creating UncertainAPI project: {project_name}")

    target_path = Path(target_dir).resolve() / project_name
    if target_path.exists():
        click.echo(f"Error: Directory {target_path} already exists", err=True)
        raise click.Abort()

    try:
        # Use Django's startproject command
        click.echo("Running django-admin startproject...")
        subprocess.run(
            [sys.executable, "-m", "django", "startproject", project_name, str(target_path)],
            check=True,
            capture_output=True,
        )

        # Customize settings.py for uncertainAPI
        settings_path = target_path / project_name / "settings.py"
        _customize_settings(settings_path, project_name)

        # Customize urls.py to include extractor app
        urls_path = target_path / project_name / "urls.py"
        _customize_urls(urls_path, project_name)

        # Create requirements.txt
        _create_requirements_file(target_path)

        # Create example extractor app
        click.echo("Creating example extractor app...")
        _create_example_app(target_path, "extractors")

        click.echo(f"✓ Project created: {target_path}")

        # Create virtual environment
        # if not no_venv:
        #     click.echo("Creating virtual environment...")
        #     _create_venv(target_path)

        # Print next steps
        click.echo("\n✨ UncertainAPI project ready!")
        click.echo("\nNext steps:")
        click.echo(f"  cd {project_name}")
        if not no_venv:
            click.echo("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        click.echo("  pip install -r requirements.txt")
        click.echo("  python manage.py migrate")
        click.echo("  python manage.py runserver")
        click.echo("\nThen visit: http://127.0.0.1:8000/api/extractors/example/")

    except subprocess.CalledProcessError as exc:
        logger.error(f"Django command failed: {exc.stderr.decode() if exc.stderr else exc}")
        click.echo(f"Error: Failed to create Django project. Make sure Django is installed.", err=True)
        if target_path.exists():
            shutil.rmtree(target_path)
        raise click.Abort()
    except Exception as exc:
        logger.exception("Failed to create project")
        click.echo(f"Error: {exc}", err=True)
        if target_path.exists():
            shutil.rmtree(target_path)
        raise click.Abort()

@main.command()
@click.argument("app_name")
@click.option("--dir", "-d", "target_dir", default=".", help="Target directory")
def startapp(app_name: str, target_dir: str) -> None:
    """Create a new extractor app.

    Creates an app with example extractors, schemas, and models.

    Example:
        uncertainapi startapp products
    """
    click.echo(f"Creating extractor app: {app_name}")

    target_path = Path(target_dir).resolve() / app_name
    if target_path.exists():
        click.echo(f"Error: Directory {target_path} already exists", err=True)
        raise click.Abort()

    try:
        # Use Django's startapp command
        subprocess.run(
            [sys.executable, "-m", "django", "startapp", app_name, str(target_path)],
            check=True,
            capture_output=True,
        )

        # Add extractor-specific files
        _add_extractor_files(target_path, app_name)

        click.echo(f"✓ App created: {target_path}")
        click.echo("\n✨ Extractor app ready!")
        click.echo("\nNext steps:")
        click.echo(f"  1. Add '{app_name}' to INSTALLED_APPS in settings.py")
        click.echo("  2. Define your extraction schema in schemas.py")
        click.echo("  3. Configure your extractor view in views.py")
        click.echo("  4. Add URL patterns to your urls.py")

    except subprocess.CalledProcessError as exc:
        logger.error(f"Django command failed: {exc.stderr.decode() if exc.stderr else exc}")
        click.echo(f"Error: Failed to create Django app. Make sure Django is installed.", err=True)
        if target_path.exists():
            shutil.rmtree(target_path)
        raise click.Abort()
    except Exception as exc:
        logger.exception("Failed to create app")
        click.echo(f"Error: {exc}", err=True)
        if target_path.exists():
            shutil.rmtree(target_path)
        raise click.Abort()

def _customize_urls(urls_path: Path, project_name: str) -> None:
    """Customize Django urls.py to include extractor app.

    Args:
        urls_path: Path to urls.py file.
        project_name: Project name.
    """
    content = urls_path.read_text()

    # Add include import
    content = content.replace(
        "from django.urls import path",
        "from django.urls import path, include"
    )

    # Add extractor app URL pattern
    content = content.replace(
        "urlpatterns = [",
        "urlpatterns = [\n    path('api/extractors/', include('extractors.urls')),"
    )

    urls_path.write_text(content)


def _customize_settings(settings_path: Path, project_name: str) -> None:
    """Customize Django settings.py for uncertainAPI.

    Args:
        settings_path: Path to settings.py file.
        project_name: Project name.
    """
    content = settings_path.read_text()

    # Add rest_framework and uncertainAPI to INSTALLED_APPS
    content = content.replace(
        "INSTALLED_APPS = [",
        "INSTALLED_APPS = [\n    'rest_framework',\n    'uncertainAPI',\n    'extractors',  # Example extractor app",
    )

    # Add uncertainAPI configuration
    uncertainapi_config = '''

# UncertainAPI Configuration
UNCERTAINAPI = {
    "AI_PROVIDER": {
        "BACKEND": "uncertainAPI.ai.providers.openai.OpenAIProvider",
        "API_KEY": os.environ.get("OPENAI_API_KEY", "your-api-key-here"),
        "MODEL": "gpt-4o",
    },
    "BROWSER_BACKEND": {
        "BACKEND": "uncertainAPI.browsers.playwright.PlaywrightBackend",
        "HEADLESS": True,
    },
    "MULTI_AGENT": {
        "ENABLED": True,
        "MAX_ROUNDS": 10,
    },
}

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}
'''

    content += uncertainapi_config
    settings_path.write_text(content)


def _create_requirements_file(target_dir: Path) -> None:
    """Create requirements.txt with uncertainAPI dependencies.

    Args:
        target_dir: Target directory.
    """
    requirements = """django>=4.2
djangorestframework>=3.14
uncertainapi[full]
python-dotenv>=1.0
"""
    (target_dir / "requirements.txt").write_text(requirements)


def _create_example_app(target_dir: Path, app_name: str) -> None:
    """Create example extractor app using Django's startapp.

    Args:
        target_dir: Project directory.
        app_name: App name.
    """
    app_path = target_dir / app_name

    # Use Django's startapp
    subprocess.run(
        [sys.executable, "-m", "django", "startapp", app_name, str(app_path)],
        check=True,
        capture_output=True,
        cwd=str(target_dir),
    )

    # Add extractor-specific files
    _add_extractor_files(app_path, app_name)


def _add_extractor_files(app_path: Path, app_name: str) -> None:
    """Add extractor-specific files to Django app.

    Args:
        app_path: Path to app directory.
        app_name: App name.
    """
    # Create schemas.py
    (app_path / "schemas.py").write_text(
        f'''"""Extraction schemas for {app_name}."""

from uncertainAPI.schemas import ExtractionSchema


class ExampleSchema(ExtractionSchema):
    """Example extraction schema.
    
    Define your data structure here using Pydantic fields.
    """

    title: str
    description: str | None = None
    price: float | None = None
'''
    )

    # Create/override views.py with extractor example
    (app_path / "views.py").write_text(
        f'''"""Extractor views for {app_name}."""

from uncertainAPI.views import ExtractorView
from .schemas import ExampleSchema


class ExampleExtractorView(ExtractorView):
    """Example extractor view.
    
    Customize this view to extract data from any website.
    """

    schema_class = ExampleSchema
    
    # Optional: Override default behavior
    # browser_backend = "playwright"
    # ai_provider = "openai"
    # use_multi_agent = True
'''
    )

    # Create urls.py for the app
    (app_path / "urls.py").write_text(
        f'''"""URL configuration for {app_name}."""

from django.urls import path
from . import views

app_name = "{app_name}"

urlpatterns = [
    path("example/", views.ExampleExtractorView.as_view(), name="example"),
]
'''
    )

def _create_venv(target_dir: Path) -> None:
    """Create virtual environment in project directory.

    Args:
        target_dir: Target directory.
    """
    import subprocess

    venv_path = target_dir / "venv"
    try:
        subprocess.run(
            ["python", "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
        )
        click.echo(f"✓ Virtual environment created: {venv_path}")
    except subprocess.CalledProcessError as exc:
        click.echo(f"Warning: Failed to create virtual environment: {exc}", err=True)

if __name__ == "__main__":
    main()

