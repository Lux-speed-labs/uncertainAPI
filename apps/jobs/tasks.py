from celery import shared_task
from datetime import datetime
import time
import logging
from .models import Job

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def execute_job(self, job_id):
    """
    Execute a background job with progress tracking and ETA updates.
    
    This task demonstrates the sync→async handoff pattern where:
    1. Job is created synchronously
    2. Background processing starts immediately 
    3. Progress is tracked via WebSocket/SSE
    4. Client can poll for updates or receive real-time notifications
    """
    try:
        job = Job.objects.get(id=job_id)
        job.status = 'started'
        job.started_at = datetime.now()
        job.celery_task_id = self.request.id
        job.save()
        
        logger.info(f"Starting job {job_id} of type {job.job_type}")
        
        # Simulate job execution based on type
        if job.job_type == 'scrape_website':
            return execute_scraping_job(self, job)
        elif job.job_type == 'process_data':
            return execute_data_processing_job(self, job)
        elif job.job_type == 'generate_report':
            return execute_report_generation_job(self, job)
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")
            
    except Job.DoesNotExist:
        logger.error(f"Job {job_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Job {job_id} failed: {str(exc)}")
        job.status = 'failure'
        job.error_message = str(exc)
        job.completed_at = datetime.now()
        job.save()
        raise


def execute_scraping_job(task, job):
    """
    Execute a web scraping job with progress updates.
    """
    steps = [
        "Initializing browser",
        "Navigating to target URL",
        "Extracting data",
        "Processing results",
        "Saving to database"
    ]
    
    job.total_steps = len(steps)
    job.save()
    
    results = {
        'url': job.input_data.get('url', ''),
        'data_extracted': [],
        'metadata': {}
    }
    
    for i, step in enumerate(steps):
        # Update progress
        job.current_step = step
        job.progress = int((i + 1) / len(steps) * 100)
        job.save()
        
        # Simulate work
        time.sleep(2)
        
        # Add step-specific results
        if step == "Extracting data":
            results['data_extracted'] = [
                {'title': 'Sample Data 1', 'content': 'Content 1'},
                {'title': 'Sample Data 2', 'content': 'Content 2'},
            ]
        elif step == "Processing results":
            results['metadata'] = {
                'items_found': len(results['data_extracted']),
                'processing_time': 10
            }
    
    # Complete the job
    job.status = 'success'
    job.result_data = results
    job.completed_at = datetime.now()
    job.progress = 100
    job.current_step = "Completed"
    job.save()
    
    logger.info(f"Scraping job {job.id} completed successfully")
    return results


def execute_data_processing_job(task, job):
    """
    Execute a data processing job.
    """
    steps = [
        "Loading input data",
        "Validating data format",
        "Processing records",
        "Generating output",
        "Finalizing results"
    ]
    
    job.total_steps = len(steps)
    job.save()
    
    input_data = job.input_data
    results = {
        'processed_records': 0,
        'errors': [],
        'output_data': []
    }
    
    for i, step in enumerate(steps):
        job.current_step = step
        job.progress = int((i + 1) / len(steps) * 100)
        job.save()
        
        time.sleep(1.5)
        
        if step == "Processing records":
            # Simulate processing
            records = input_data.get('records', [])
            results['processed_records'] = len(records)
            results['output_data'] = [f"processed_{i}" for i in range(len(records))]
    
    job.status = 'success'
    job.result_data = results
    job.completed_at = datetime.now()
    job.progress = 100
    job.current_step = "Completed"
    job.save()
    
    logger.info(f"Data processing job {job.id} completed successfully")
    return results


def execute_report_generation_job(task, job):
    """
    Execute a report generation job.
    """
    steps = [
        "Gathering data sources",
        "Analyzing data",
        "Creating visualizations",
        "Generating report",
        "Exporting to file"
    ]
    
    job.total_steps = len(steps)
    job.save()
    
    results = {
        'report_id': f"report_{job.id}",
        'file_path': f"/reports/report_{job.id}.pdf",
        'statistics': {}
    }
    
    for i, step in enumerate(steps):
        job.current_step = step
        job.progress = int((i + 1) / len(steps) * 100)
        job.save()
        
        time.sleep(2)
        
        if step == "Analyzing data":
            results['statistics'] = {
                'total_records': 1000,
                'processed': 950,
                'errors': 50
            }
    
    job.status = 'success'
    job.result_data = results
    job.completed_at = datetime.now()
    job.progress = 100
    job.current_step = "Completed"
    job.save()
    
    logger.info(f"Report generation job {job.id} completed successfully")
    return results