"""
Load testing with Locust.

Sprint 5 Week 4: Performance Testing

Usage:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Tests:
- 10 concurrent users
- 50 concurrent users
- 100 concurrent users
- Spike testing
"""

from locust import HttpUser, task, between
import random


class BotUser(HttpUser):
    """Simulated bot user for load testing."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when user starts."""
        self.user_id = random.randint(1000, 9999)
        self.messages = [
            "Привет, мне нужна помощь.",
            "Мне очень тяжело.",
            "Что мне делать?",
            "Спасибо за поддержку.",
        ]
        self.message_index = 0

    @task(weight=10)
    def send_message(self):
        """Send a message to bot."""
        message = self.messages[self.message_index % len(self.messages)]
        self.message_index += 1

        # Simulated API call
        # In real implementation, replace with actual bot endpoint
        # self.client.post("/api/message", json={
        #     "user_id": self.user_id,
        #     "message": message
        # })
        pass

    @task(weight=2)
    def check_status(self):
        """Check bot status."""
        # self.client.get("/api/status")
        pass


class StressTestUser(HttpUser):
    """Stress test with rapid requests."""

    wait_time = between(0.1, 0.5)  # Very fast requests

    @task
    def rapid_messages(self):
        """Send rapid messages."""
        pass


# Performance targets:
# - Response time < 2s (p95)
# - Support 100 concurrent users
# - Error rate < 1%
# - No memory leaks
