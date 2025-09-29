#!/usr/bin/env python3
"""
UncertainAPI Usage Examples

This script demonstrates how to use the UncertainAPI endpoints
with example requests and expected responses.
"""

import json

def show_api_examples():
    """Show example API requests and responses."""
    
    print("🌐 UncertainAPI Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "title": "Health Check",
            "method": "GET",
            "url": "/api/v1/health/",
            "description": "Check if the API is running",
            "request": None,
            "response": {
                "status": "healthy",
                "message": "UncertainAPI is running"
            }
        },
        {
            "title": "Start Web Scraping Job",
            "method": "POST", 
            "url": "/api/v1/scrape/",
            "description": "Start a web scraping job with auto sync→async handoff",
            "request": {
                "url": "https://httpbin.org/html",
                "wait_time": 5,
                "extract_links": True,
                "extract_text": True,
                "css_selectors": [".content", "h1"]
            },
            "response": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending", 
                "estimated_completion": "2024-01-01T12:05:00Z",
                "websocket_url": "/ws/jobs/123e4567-e89b-12d3-a456-426614174000/progress/"
            }
        },
        {
            "title": "Create Background Job",
            "method": "POST",
            "url": "/api/v1/jobs/",
            "description": "Create a custom background job",
            "request": {
                "job_type": "data_processing",
                "input_data": {
                    "records": [
                        {"id": 1, "name": "John"},
                        {"id": 2, "name": "Jane"}
                    ]
                },
                "estimated_duration": 300
            },
            "response": {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "status": "pending",
                "job_type": "data_processing", 
                "progress": 0,
                "estimated_completion": "2024-01-01T12:05:00Z"
            }
        },
        {
            "title": "Get Job Status",
            "method": "GET",
            "url": "/api/v1/jobs/{job_id}/",
            "description": "Get detailed job status with progress and ETA",
            "request": None,
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "started",
                "job_type": "scrape_website",
                "progress": 60,
                "current_step": "Extracting data",
                "total_steps": 5,
                "estimated_completion": "2024-01-01T12:03:30Z",
                "is_running": True
            }
        },
        {
            "title": "List All Jobs",
            "method": "GET", 
            "url": "/api/v1/jobs/?status=pending",
            "description": "List jobs with optional filtering",
            "request": None,
            "response": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "pending",
                    "job_type": "scrape_website",
                    "progress": 0
                }
            ]
        },
        {
            "title": "Cancel Job",
            "method": "POST",
            "url": "/api/v1/jobs/{job_id}/cancel/",
            "description": "Cancel a running job",
            "request": None,
            "response": {
                "message": "Job cancelled successfully"
            }
        },
        {
            "title": "MCP Server Health", 
            "method": "GET",
            "url": "/mcp/health/",
            "description": "Check MCP server status",
            "request": None,
            "response": {
                "status": "healthy",
                "mcp_version": "1.0.0",
                "server_info": {
                    "name": "UncertainAPI MCP Server",
                    "version": "1.0.0"
                }
            }
        },
        {
            "title": "MCP Capabilities",
            "method": "GET", 
            "url": "/mcp/capabilities/",
            "description": "Get MCP server capabilities",
            "request": None,
            "response": {
                "capabilities": {
                    "tools": [
                        {
                            "name": "web_scraper",
                            "description": "Scrape web pages using Playwright"
                        }
                    ],
                    "resources": ["jobs", "scraped_data"]
                }
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print("-" * (len(example['title']) + 3))
        print(f"📝 {example['description']}")
        print()
        print(f"🔗 {example['method']} {example['url']}")
        
        if example['request']:
            print("\n📤 Request Body:")
            print(json.dumps(example['request'], indent=2))
        
        print("\n📥 Response:")
        print(json.dumps(example['response'], indent=2))
        print()

def show_websocket_example():
    """Show WebSocket usage example."""
    
    print("\n🔌 WebSocket Real-time Progress Updates")
    print("=" * 45)
    
    print("""
📡 JavaScript Example:

const jobId = '123e4567-e89b-12d3-a456-426614174000';
const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${jobId}/progress/`);

ws.onopen = function(event) {
    console.log('Connected to job progress updates');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'progress_update') {
        console.log(`Progress: ${data.progress}%`);
        console.log(`Current step: ${data.current_step}`);
        console.log(`ETA: ${data.estimated_completion}`);
    }
    
    if (data.type === 'job_completed') {
        console.log('Job completed!');
        console.log('Results:', data.result_data);
        ws.close();
    }
};

📡 Python Example (using websockets library):

import asyncio
import websockets
import json

async def monitor_job_progress(job_id):
    uri = f"ws://localhost:8000/ws/jobs/{job_id}/progress/"
    
    async with websockets.connect(uri) as websocket:
        print(f"Monitoring job {job_id}...")
        
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'progress_update':
                print(f"Progress: {data['progress']}% - {data['current_step']}")
            
            elif data['type'] == 'job_completed':
                print("Job completed!")
                print("Results:", data['result_data'])
                break

# Usage
asyncio.run(monitor_job_progress('123e4567-e89b-12d3-a456-426614174000'))
""")

def show_curl_examples():
    """Show curl command examples."""
    
    print("\n🌐 cURL Command Examples")
    print("=" * 30)
    
    curl_commands = [
        {
            "title": "Health Check",
            "command": "curl -X GET http://localhost:8000/api/v1/health/"
        },
        {
            "title": "Start Scraping Job", 
            "command": """curl -X POST http://localhost:8000/api/v1/scrape/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN" \\
  -d '{
    "url": "https://httpbin.org/html",
    "wait_time": 5,
    "extract_links": true,
    "extract_text": true
  }'"""
        },
        {
            "title": "Get Job Status",
            "command": """curl -X GET http://localhost:8000/api/v1/jobs/JOB_ID/ \\
  -H "Authorization: Token YOUR_TOKEN" """
        },
        {
            "title": "List Jobs",
            "command": """curl -X GET "http://localhost:8000/api/v1/jobs/?status=pending" \\
  -H "Authorization: Token YOUR_TOKEN" """
        },
        {
            "title": "Create Custom Job",
            "command": """curl -X POST http://localhost:8000/api/v1/jobs/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN" \\
  -d '{
    "job_type": "data_processing",
    "input_data": {"records": [{"id": 1, "name": "Test"}]}
  }'"""
        },
        {
            "title": "Idempotent Request (with retry safety)",
            "command": """curl -X POST http://localhost:8000/api/v1/scrape/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN" \\
  -H "Idempotency-Key: unique-key-123" \\
  -d '{"url": "https://example.com"}'"""
        }
    ]
    
    for i, cmd in enumerate(curl_commands, 1):
        print(f"\n{i}. {cmd['title']}:")
        print(cmd['command'])

def show_docker_setup():
    """Show Docker setup instructions."""
    
    print("\n🐳 Docker Setup & Deployment")
    print("=" * 35)
    
    print("""
🚀 Quick Start with Docker:

# 1. Clone repository and setup environment
git clone <repository-url>
cd uncertainAPI
cp .env.example .env

# 2. Start all services 
make docker-up

# 3. Services will be available at:
# - API: http://localhost:8000/api/v1/
# - Docs: http://localhost:8000/api/docs/
# - Admin: http://localhost:8000/admin/
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379

# 4. Create superuser (in new terminal)
docker-compose exec web python manage.py createsuperuser

# 5. Run tests
docker-compose exec web pytest

# 6. View logs
make docker-logs

# 7. Stop services
make docker-down

🔧 Local Development:

# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# 2. Install dependencies
make install

# 3. Setup database
make migrate
make superuser

# 4. Start development servers (separate terminals)
make run          # Django development server
make celery       # Celery worker for background tasks
make celery-beat  # Celery beat scheduler (optional)

# 5. Run tests
make test
""")

def main():
    """Main function to display all examples."""
    
    show_api_examples()
    show_websocket_example()
    show_curl_examples()
    show_docker_setup()
    
    print("\n" + "=" * 60)
    print("🎯 Key Features Demonstrated:")
    print("• Sync→Async handoff: Immediate response + background processing")
    print("• Real-time progress: WebSocket updates with ETA")
    print("• Idempotency: Safe request retries")
    print("• Comprehensive API: REST endpoints + WebSocket + MCP")
    print("• Production ready: Docker, tests, monitoring")
    print("=" * 60)

if __name__ == '__main__':
    main()