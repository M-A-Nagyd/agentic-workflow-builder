import time
from typing import Callable, List


class LLMProviderError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.open_until = None

    def allow(self) -> bool:
        if self.open_until is None:
            return True
        if time.time() > self.open_until:
            # reset breaker
            self.failure_count = 0
            self.open_until = None
            return True
        return False

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.open_until = time.time() + self.reset_timeout

    def record_success(self):
        self.failure_count = 0
        self.open_until = None


class LLMRouter:
    def __init__(self, providers: List[Callable[[str, str], str]]):
        self.providers = providers
        self.breakers = {provider: CircuitBreaker() for provider in providers}

    def call(self, model: str, prompt: str) -> str:
        last_error = None

        for provider in self.providers:
            breaker = self.breakers[provider]

            if not breaker.allow():
                continue

            try:
                result = provider(model, prompt)
                breaker.record_success()
                return result

            except Exception as e:
                breaker.record_failure()
                last_error = e
                continue

        raise LLMProviderError(
            f"All LLM providers failed. Last error: {last_error}"
        )
