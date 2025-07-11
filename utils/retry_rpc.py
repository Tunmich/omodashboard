import time
import logging

def retry_rpc_call(func, max_attempts=3, base_delay=2, *args, **kwargs):
    """
    Retry any RPC call with exponential backoff.
    - func: the callable to execute
    - max_attempts: total retries before failing
    - base_delay: delay in seconds between attempts
    - args/kwargs: passed to the target func
    """
    attempt = 1
    while attempt <= max_attempts:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"⚠️ RPC call failed on attempt {attempt}: {e}")
            if attempt == max_attempts:
                logging.error(f"❌ RPC failed permanently after {max_attempts} attempts.")
                raise e
            time.sleep(base_delay * attempt)  # Exponential backoff
            attempt += 1