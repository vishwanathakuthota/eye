from __future__ import annotations

import logging
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)


def retry_call[T](
    operation: Callable[[], T],
    *,
    attempts: int,
    delay_seconds: float,
    source: str,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except retry_exceptions as exc:
            last_error = exc
            if attempt == attempts:
                break
            logger.warning(
                "external_source_retry",
                extra={"source": source, "attempt": attempt},
            )
            time.sleep(delay_seconds * attempt)

    if last_error is None:
        raise RuntimeError("Retry operation failed without an exception.")
    raise last_error
