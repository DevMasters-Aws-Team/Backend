import time
import json
import structlog
from collections import deque
from typing import List, Dict, Any
from src.config import settings
from src.utils.aws_helpers import get_boto3_client
from src.models.logs import StructuredLogEvent

logger = structlog.get_logger()

class CloudWatchClient:
    """
    AWS CloudWatch Logs Integration Client.
    Emits structured JSON log events to CloudWatch Logs group and maintains
    an in-memory buffer for local telemetry inspection.
    """
    def __init__(self) -> None:
        self.log_group_name = settings.LOG_GROUP_NAME
        self.log_stream_name = "e-commerce-stream"
        self._logs_buffer: List[Dict[str, Any]] = []
        self._recent_events: deque = deque(maxlen=2000)

    def emit_log(self, event: StructuredLogEvent) -> None:
        """Logs structured JSON to stdout, stores in local memory buffer, and queues for CloudWatch."""
        log_dict = event.model_dump()
        self._recent_events.appendleft(event)
        
        if event.level == "ERROR":
            logger.error("microservice_event", **log_dict)
        elif event.level == "WARN":
            logger.warning("microservice_event", **log_dict)
        else:
            logger.info("microservice_event", **log_dict)
            
        self._logs_buffer.append({
            'timestamp': int(time.time() * 1000),
            'message': json.dumps(log_dict)
        })

    def get_recent_logs(self, limit: int = 1000) -> List[StructuredLogEvent]:
        """Returns recent structured log events stored in local memory."""
        return list(self._recent_events)[:limit]

    def flush_to_cloudwatch(self) -> int:
        """Sends buffered log events to AWS CloudWatch Logs via boto3."""
        if not self._logs_buffer:
            return 0
        count = len(self._logs_buffer)
        try:
            client = get_boto3_client('logs')
            client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=self._logs_buffer[:100]
            )
        except Exception:
            # Fallback gracefully if CloudWatch is unavailable or running locally
            pass
        finally:
            self._logs_buffer.clear()
        return count

cloudwatch_client = CloudWatchClient()
