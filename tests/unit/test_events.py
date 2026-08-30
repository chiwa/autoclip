from app.domain.events import JobEvent, JobEventPublisher, JobEventType


def test_event_sse_format_supports_unicode():
    value = JobEvent(type=JobEventType.LOG, job_id="one", payload={"message": "ภาษาไทย"}).to_sse()
    assert value.startswith("event: log\ndata: ")
    assert "ภาษาไทย" in value
    assert value.endswith("\n\n")


def test_heartbeat_format():
    value = JobEvent(type=JobEventType.HEARTBEAT, job_id="one").to_sse()
    assert value == "event: heartbeat\ndata: {}\n\n"


def test_multiple_subscribers_receive_event_and_disconnect_cleanup():
    publisher = JobEventPublisher()
    with publisher.subscribe("one") as first, publisher.subscribe("one") as second:
        publisher.publish(JobEvent(type=JobEventType.PROGRESS, job_id="one", payload={"progress": 42}))
        assert first.get_nowait().payload["progress"] == 42
        assert second.get_nowait().payload["progress"] == 42
        assert publisher.subscriber_count("one") == 2
    assert publisher.subscriber_count("one") == 0


def test_bounded_subscriber_drops_oldest_event():
    publisher = JobEventPublisher(subscriber_queue_size=1)
    with publisher.subscribe("one") as subscriber:
        publisher.publish(JobEvent(type=JobEventType.LOG, job_id="one", payload={"message": "old"}))
        publisher.publish(JobEvent(type=JobEventType.COMPLETED, job_id="one", payload={"status": "COMPLETED"}))
        assert subscriber.get_nowait().type == JobEventType.COMPLETED


def test_all_business_event_types_are_published():
    publisher = JobEventPublisher()
    expected = [JobEventType.PROGRESS, JobEventType.LOG, JobEventType.COMPLETED, JobEventType.FAILED]
    with publisher.subscribe("one") as subscriber:
        for event_type in expected:
            publisher.publish(JobEvent(type=event_type, job_id="one"))
        assert [subscriber.get_nowait().type for _ in expected] == expected
