#!/bin/bash
# Quick setup script for local development

set -e  # Exit on error

echo "🚀 UncertainAPI Local Setup"
echo "============================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "❌ Python 3.8+ required"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "📦 Installing UncertainAPI in editable mode..."
cd "$SCRIPT_DIR"

# Offer installation options
echo ""
echo "Choose installation option:"
echo "1) Full install (all extras)"
echo "2) Minimal install (core only)"
echo "3) Custom install (select extras)"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo "Installing with all extras..."
        pip install -e ".[full]"
        ;;
    2)
        echo "Installing core only..."
        pip install -e .
        ;;
    3)
        echo "Available extras: playwright, selenium, requests, openai, anthropic, litellm, celery, django-q"
        read -p "Enter extras (comma-separated): " extras
        pip install -e ".[$extras]"
        ;;
    *)
        echo "Invalid choice, installing core only..."
        pip install -e .
        ;;
esac

echo ""
echo "✓ Installation complete!"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if command -v uncertainapi &> /dev/null; then
    echo "✓ uncertainapi CLI is available"
    uncertainapi --version
else
    echo "❌ uncertainapi CLI not found in PATH"
    echo "   Try: pip install -e ."
    exit 1
fi

# Optional: Install Playwright browsers
if pip list | grep -q playwright; then
    echo ""
    read -p "Install Playwright browsers? [y/N]: " install_browsers
    if [[ $install_browsers =~ ^[Yy]$ ]]; then
        echo "Installing Playwright browsers..."
        playwright install chromium
        echo "✓ Playwright browsers installed"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a new project:"
echo "   uncertainapi createproject myproject"
echo ""
echo "2. Navigate to project:"
echo "   cd myproject"
echo ""
echo "3. Configure settings.py with your API keys"
echo ""
echo "4. Create an app:"
echo "   uncertainapi startapp myapp"
echo ""
echo "5. Run with ASGI server:"
echo "   uvicorn myproject.asgi:application --reload"
echo ""
echo "📖 See GETTING_STARTED_LOCAL.md for detailed guide"



