"""Task runner functions."""

from __future__ import annotations

from loguru import logger
from typing import Any

async def run_extraction_task(
    view_path: str,
    url: str,
    schema_json: str,
    task_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a extractor task in the background.

    Args:
        view_path: Dotted path to ExtractorView class.
        url: URL to extract.
        schema_json: JSON schema as string.
        task_id: Task ID for tracking.
        **kwargs: Additional parameters.

    Returns:
        Result dictionary.
    """
    from uncertainAPI.models import ExtractionTask

    logger.info("task.run.start", extra={"task_id": task_id, "url": url})

    try:
        # Get task instance
        task = ExtractionTask.objects.get(id=task_id)
        task.mark_running()

        # TODO: Implement actual task execution
        # This would:
        # 1. Import the view class
        # 2. Create orchestrator
        # 3. Run extraction
        # 4. Save results

        result = {"status": "success", "data": []}

        task.mark_completed(result)
        return result

    except Exception as exc:
        logger.exception("task.run.failed", extra={"task_id": task_id})
        try:
            task = ExtractionTask.objects.get(id=task_id)
            task.mark_failed(str(exc))
        except Exception:
            pass
        raise

