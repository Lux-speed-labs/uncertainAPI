import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.jobs.models import Job


@pytest.mark.django_db
class TestJobAPI:
    """
    Test cases for the Job API endpoints.
    """
    
    def setup_method(self):
        """Setup test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_job(self):
        """Test creating a new job."""
        data = {
            'job_type': 'scrape_website',
            'input_data': {'url': 'https://example.com'}
        }
        
        response = self.client.post('/api/v1/jobs/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['job_type'] == 'scrape_website'
        assert response.data['status'] == 'pending'
    
    def test_list_jobs(self):
        """Test listing jobs."""
        # Create a test job
        job = Job.objects.create(
            job_type='test_job',
            created_by=self.user,
            input_data={'test': 'data'}
        )
        
        response = self.client.get('/api/v1/jobs/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == str(job.id)
    
    def test_get_job_detail(self):
        """Test getting job details."""
        job = Job.objects.create(
            job_type='test_job',
            created_by=self.user,
            input_data={'test': 'data'}
        )
        
        response = self.client.get(f'/api/v1/jobs/{job.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(job.id)
        assert response.data['job_type'] == 'test_job'


@pytest.mark.django_db
class TestScrapeAPI:
    """
    Test cases for the Scrape API endpoint.
    """
    
    def setup_method(self):
        """Setup test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_scrape_endpoint(self):
        """Test the scrape endpoint."""
        data = {
            'url': 'https://httpbin.org/html',
            'wait_time': 2,
            'extract_links': True,
            'extract_text': True
        }
        
        response = self.client.post('/api/v1/scrape/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'job_id' in response.data
        assert 'websocket_url' in response.data
        assert response.data['status'] == 'pending'
    
    def test_scrape_invalid_url(self):
        """Test scraping with invalid URL."""
        data = {
            'url': 'not-a-valid-url',
        }
        
        response = self.client.post('/api/v1/scrape/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCoreAPI(TestCase):
    """
    Test cases for core API endpoints.
    """
    
    def setUp(self):
        """Setup test data."""
        self.client = APIClient()
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/api/v1/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_api_root(self):
        """Test the API root endpoint."""
        response = self.client.get('/api/v1/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('endpoints', response.data)
        self.assertIn('version', response.data)


class TestMCPEndpoints(TestCase):
    """
    Test cases for MCP server endpoints.
    """
    
    def setUp(self):
        """Setup test data."""
        self.client = APIClient()
    
    def test_mcp_health(self):
        """Test MCP health endpoint."""
        response = self.client.get('/mcp/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('mcp_version', response.data)
    
    def test_mcp_capabilities(self):
        """Test MCP capabilities endpoint."""
        response = self.client.get('/mcp/capabilities/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('capabilities', response.data)
        self.assertIn('tools', response.data['capabilities'])
        self.assertIn('resources', response.data['capabilities'])


if __name__ == '__main__':
    pytest.main([__file__])