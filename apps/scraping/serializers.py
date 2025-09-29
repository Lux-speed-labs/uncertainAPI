from rest_framework import serializers


class ScrapeRequestSerializer(serializers.Serializer):
    """
    Serializer for web scraping requests.
    """
    url = serializers.URLField(
        help_text="The URL to scrape"
    )
    wait_time = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=30,
        help_text="Time to wait for page load (seconds)"
    )
    extract_links = serializers.BooleanField(
        default=True,
        help_text="Whether to extract all links from the page"
    )
    extract_images = serializers.BooleanField(
        default=False,
        help_text="Whether to extract image URLs"
    )
    extract_text = serializers.BooleanField(
        default=True,
        help_text="Whether to extract text content"
    )
    css_selectors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="CSS selectors for specific elements to extract"
    )
    javascript_enabled = serializers.BooleanField(
        default=True,
        help_text="Whether to enable JavaScript execution"
    )
    user_agent = serializers.CharField(
        required=False,
        help_text="Custom user agent string"
    )
    headers = serializers.DictField(
        required=False,
        help_text="Additional HTTP headers"
    )
    
    def validate_url(self, value):
        """
        Validate that the URL is accessible and safe to scrape.
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise serializers.ValidationError("Invalid URL format")
        
        if parsed.scheme not in ['http', 'https']:
            raise serializers.ValidationError("Only HTTP and HTTPS URLs are supported")
        
        # Block internal/private URLs
        import ipaddress
        try:
            # Check if it's an IP address
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback:
                raise serializers.ValidationError("Cannot scrape private or localhost URLs")
        except ValueError:
            # Not an IP address, check for localhost
            if parsed.hostname in ['localhost', '127.0.0.1', '::1']:
                raise serializers.ValidationError("Cannot scrape localhost URLs")
        
        return value


class ScrapeResponseSerializer(serializers.Serializer):
    """
    Serializer for web scraping responses.
    """
    job_id = serializers.UUIDField(
        help_text="ID of the background job processing this request"
    )
    status = serializers.CharField(
        help_text="Current status of the scraping job"
    )
    estimated_completion = serializers.DateTimeField(
        help_text="Estimated completion time"
    )
    websocket_url = serializers.CharField(
        help_text="WebSocket URL for real-time progress updates"
    )