# analytics_mcp/utils/google_retry.py
import time
import random
from googleapiclient.errors import HttpError

TRANSIENT_CODES = {429, 500, 502, 503, 504}

def call_with_retry(request_exec, *, retries=5, base=0.5, cap=8.0):
    """
    request_exec: a lambda that executes the googleapiclient request .execute()
    """
    attempt = 0
    while True:
        try:
            return request_exec()
        except HttpError as e:
            code = getattr(e, "status_code", None) or (e.resp.status if hasattr(e, "resp") else None)
            if code in TRANSIENT_CODES and attempt < retries:
                sleep_s = min(cap, base * (2 ** attempt)) + random.uniform(0, 0.25)
                time.sleep(sleep_s)
                attempt += 1
                continue
            raise
