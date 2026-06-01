from collections import defaultdict, deque
from time import monotonic


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._attempts: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(
        self,
        *,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        now = monotonic()
        attempts = self._attempts[key]

        while attempts and now - attempts[0] > window_seconds:
            attempts.popleft()

        if len(attempts) >= limit:
            return False

        attempts.append(now)
        return True

    def reset(self, *, key: str) -> None:
        self._attempts.pop(key, None)


rate_limiter = InMemoryRateLimiter()