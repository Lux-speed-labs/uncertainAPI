"""
Playwright-based web scraping utilities.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """
    Playwright-based web scraper with configurable options.
    """
    
    def __init__(self, headless: bool = True, browser_type: str = 'chromium'):
        self.headless = headless
        self.browser_type = browser_type
        self.browser = None
        self.context = None
        self.page = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self):
        """Initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            if self.browser_type == 'chromium':
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            logger.info(f"Playwright {self.browser_type} browser started")
            
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright")
            raise
        except Exception as e:
            logger.error(f"Failed to start Playwright browser: {e}")
            raise
    
    async def close(self):
        """Close Playwright browser."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("Playwright browser closed")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def scrape_page(self, 
                         url: str,
                         wait_time: int = 5,
                         extract_links: bool = True,
                         extract_images: bool = False,
                         extract_text: bool = True,
                         css_selectors: Optional[List[str]] = None,
                         user_agent: Optional[str] = None,
                         headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Scrape a web page with configurable extraction options.
        
        Args:
            url: URL to scrape
            wait_time: Time to wait for page load
            extract_links: Whether to extract links
            extract_images: Whether to extract image URLs
            extract_text: Whether to extract text content
            css_selectors: CSS selectors for specific elements
            user_agent: Custom user agent
            headers: Additional headers
            
        Returns:
            Dictionary containing extracted data
        """
        if not self.page:
            raise RuntimeError("Browser not started. Use async context manager or call start()")
        
        try:
            # Set custom user agent if provided
            if user_agent:
                await self.page.set_extra_http_headers({'User-Agent': user_agent})
            
            # Set additional headers if provided
            if headers:
                await self.page.set_extra_http_headers(headers)
            
            # Navigate to the page
            logger.info(f"Navigating to {url}")
            response = await self.page.goto(url, wait_until='networkidle')
            
            if not response.ok:
                raise Exception(f"HTTP {response.status}: {response.status_text}")
            
            # Wait for page load
            await asyncio.sleep(wait_time)
            
            # Extract data
            result = {
                'url': url,
                'title': await self.page.title(),
                'status_code': response.status,
                'final_url': self.page.url,
                'metadata': {
                    'load_time': wait_time,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Extract text content
            if extract_text:
                result['text'] = await self.page.inner_text('body')
                result['html'] = await self.page.content()
            
            # Extract links
            if extract_links:
                links = await self.page.evaluate('''
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(link => ({
                            text: link.textContent.trim(),
                            href: link.href,
                            title: link.title || null
                        }));
                    }
                ''')
                result['links'] = links
            
            # Extract images
            if extract_images:
                images = await self.page.evaluate('''
                    () => {
                        const images = Array.from(document.querySelectorAll('img[src]'));
                        return images.map(img => ({
                            src: img.src,
                            alt: img.alt || null,
                            title: img.title || null
                        }));
                    }
                ''')
                result['images'] = images
            
            # Extract specific elements by CSS selectors
            if css_selectors:
                result['selected_elements'] = {}
                for selector in css_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        element_data = []
                        for element in elements:
                            text = await element.inner_text()
                            html = await element.inner_html()
                            element_data.append({
                                'text': text,
                                'html': html
                            })
                        result['selected_elements'][selector] = element_data
                    except Exception as e:
                        logger.warning(f"Failed to extract selector '{selector}': {e}")
                        result['selected_elements'][selector] = []
            
            logger.info(f"Successfully scraped {url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise


def run_scraping_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a scraping job synchronously (for use in Celery tasks).
    
    Args:
        job_data: Dictionary containing scraping parameters
        
    Returns:
        Dictionary containing scraped data
    """
    async def _scrape():
        async with PlaywrightScraper() as scraper:
            return await scraper.scrape_page(**job_data)
    
    # Run the async function in a new event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_scrape())