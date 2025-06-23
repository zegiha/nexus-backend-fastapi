import functools
import random
import asyncio


def retry(max_retries=10):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if any(code in str(e).lower() for code in ["592", "529", "overloaded", "anthropicerror"]) and i < max_retries - 1:
                        wait_time = (2 ** i) + random.uniform(0, 1)
                        print(f"592 에러 발생, {wait_time:.1f}초 대기...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            return None
        return wrapper
    return decorator

