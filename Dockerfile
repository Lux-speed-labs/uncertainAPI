FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database\n\
echo "Waiting for database..."\n\
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do\n\
  echo "Database is unavailable - sleeping"\n\
  sleep 1\n\
done\n\
echo "Database is available"\n\
\n\
# Run migrations\n\
python manage.py migrate\n\
\n\
# Collect static files\n\
python manage.py collectstatic --noinput\n\
\n\
# Start server\n\
exec "$@"' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "uncertainapi.wsgi:application"]