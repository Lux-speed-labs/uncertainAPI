from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)


class JobProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time job progress updates.
    """
    
    async def connect(self):
        """
        Accept WebSocket connection and join job progress group.
        """
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.job_group_name = f'job_progress_{self.job_id}'
        
        # Join job progress group
        await self.channel_layer.group_add(
            self.job_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for job {self.job_id}")
    
    async def disconnect(self, close_code):
        """
        Leave job progress group.
        """
        await self.channel_layer.group_discard(
            self.job_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for job {self.job_id}")
    
    async def receive(self, text_data):
        """
        Handle messages from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    async def job_progress_update(self, event):
        """
        Handle job progress updates from the group.
        """
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'job_id': event['job_id'],
            'status': event['status'],
            'progress': event['progress'],
            'current_step': event['current_step'],
            'estimated_completion': event.get('estimated_completion'),
            'result_data': event.get('result_data'),
            'error_message': event.get('error_message'),
        }))
    
    async def job_completed(self, event):
        """
        Handle job completion notifications.
        """
        await self.send(text_data=json.dumps({
            'type': 'job_completed',
            'job_id': event['job_id'],
            'status': event['status'],
            'result_data': event.get('result_data'),
            'error_message': event.get('error_message'),
        }))


# Helper functions for sending updates from tasks
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_job_progress_update(job):
    """
    Send job progress update to WebSocket subscribers.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'job_progress_{job.id}',
            {
                'type': 'job_progress_update',
                'job_id': str(job.id),
                'status': job.status,
                'progress': job.progress,
                'current_step': job.current_step,
                'estimated_completion': job.estimated_completion.isoformat() if job.estimated_completion else None,
                'result_data': job.result_data if job.is_completed else None,
                'error_message': job.error_message if job.status == 'failure' else None,
            }
        )

def send_job_completion(job):
    """
    Send job completion notification to WebSocket subscribers.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'job_progress_{job.id}',
            {
                'type': 'job_completed',
                'job_id': str(job.id),
                'status': job.status,
                'result_data': job.result_data,
                'error_message': job.error_message if job.status == 'failure' else None,
            }
        )