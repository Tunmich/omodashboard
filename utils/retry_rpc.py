import time
import logging

def retry_rpc_call(func, max_attempts=3, base_delay=2, fallback=None, context="", *args, **kwargs):
    """
    Retry any RPC call with exponential backoff.
    
    Parameters:
    - func: the callable to execute
    - max_attempts: total retries before failing
    - base_delay: delay in seconds between attempts
    - fallback: optional fallback function if primary fails
    - context: string label for logging context
    - args/kwargs: passed to the target func
    """
    attempt = 1
    while attempt <= max_attempts:
        try:
            result = func(*args, **kwargs)
            logging.info(f"✅ RPC success [{context}] on attempt {attempt}")
            return result
        except Exception as e:
            logging.warning(f"⚠️ RPC failed [{context}] attempt {attempt}: {e}")
            if attempt == max_attempts:
                logging.error(f"❌ RPC permanently failed [{context}] after {max_attempts} attempts.")
                if fallback:
                    logging.info(f"🔁 Executing fallback for [{context}]...")
                    try:
                        return fallback(*args, **kwargs)
                    except Exception as fe:
                        logging.error(f"❌ Fallback failed [{context}]: {fe}")
                        raise fe
                raise e
            time.sleep(base_delay * attempt)
            attempt += 1
