from time import perf_counter
import functools
import inspect


def timer(func):
    """Decorator to measure the execution time of sync or async functions."""

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        """Synchronous wrapper to measure execution time."""
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"{func.__name__} (sync) took {end - start:.4f} seconds")
        return result

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        """Asynchronous wrapper to measure execution time."""
        start = perf_counter()
        result = await func(*args, **kwargs)
        end = perf_counter()
        print(f"{func.__name__} (async) took {end - start:.4f} seconds")
        return result

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
