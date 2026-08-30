from __future__ import annotations

import json
import queue
import threading
from contextlib import contextmanager
from datetime import datetime
from enum import StrEnum
from typing import Iterator

from pydantic import BaseModel, Field


def local_now() -> datetime:
    return datetime.now().astimezone()


class JobEventType(StrEnum):
    PROGRESS = "progress"
    LOG = "log"
    COMPLETED = "completed"
    FAILED = "failed"
    HEARTBEAT = "heartbeat"


class JobEvent(BaseModel):
    type: JobEventType
    job_id: str
    timestamp: datetime = Field(default_factory=local_now)
    payload: dict = Field(default_factory=dict)

    def to_sse(self) -> str:
        data = json.dumps(self.payload, ensure_ascii=False, separators=(",", ":"))
        return f"event: {self.type.value}\ndata: {data}\n\n"


class JobEventPublisher:
    """Transport-neutral, in-memory fan-out for active job subscribers."""

    def __init__(self, subscriber_queue_size: int = 256):
        self._subscribers: dict[str, set[queue.Queue[JobEvent]]] = {}
        self._lock = threading.Lock()
        self._queue_size = subscriber_queue_size

    def publish(self, event: JobEvent) -> None:
        with self._lock:
            subscribers = tuple(self._subscribers.get(event.job_id, ()))
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(event)
            except queue.Full:
                try:
                    subscriber.get_nowait()
                    subscriber.put_nowait(event)
                except (queue.Empty, queue.Full):
                    pass

    @contextmanager
    def subscribe(self, job_id: str) -> Iterator[queue.Queue[JobEvent]]:
        subscriber: queue.Queue[JobEvent] = queue.Queue(maxsize=self._queue_size)
        with self._lock:
            self._subscribers.setdefault(job_id, set()).add(subscriber)
        try:
            yield subscriber
        finally:
            with self._lock:
                subscribers = self._subscribers.get(job_id)
                if subscribers is not None:
                    subscribers.discard(subscriber)
                    if not subscribers:
                        self._subscribers.pop(job_id, None)

    def subscriber_count(self, job_id: str) -> int:
        with self._lock:
            return len(self._subscribers.get(job_id, ()))

