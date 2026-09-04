from collections import defaultdict
from time import monotonic
from fastapi import HTTPException, Request

_windows: dict[str, list[float]] = defaultdict(list)

def enforce_rate_limit(request: Request, key: str, limit: int, window_seconds: int = 60):
    now = monotonic()
    if len(_windows) > 10000:
        for stale_key in [name for name, stamps in _windows.items() if not stamps or now - stamps[-1] >= window_seconds]:
            _windows.pop(stale_key, None)
    bucket = [stamp for stamp in _windows[key] if now - stamp < window_seconds]
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    bucket.append(now)
    _windows[key] = bucket