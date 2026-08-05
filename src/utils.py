import logging
import time
from functools import wraps
from pathlib import Path

def setup_logger(name: str, log_file: Path = None, level=logging.INFO):
    """Set up logger to log to console and optionally to a file."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup multiple times
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

def timer_decorator(logger=None):
    """Decorator to measure and log execution time of a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            if logger:
                logger.info(f"Starting execution of '{func.__name__}'...")
            else:
                print(f"Starting execution of '{func.__name__}'...")
                
            result = func(*args, **kwargs)
            
            elapsed_time = time.time() - start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            time_str = f"{int(hours)}h {int(minutes)}m {seconds:.2f}s" if hours > 0 else (f"{int(minutes)}m {seconds:.2f}s" if minutes > 0 else f"{seconds:.2f}s")
            
            if logger:
                logger.info(f"Finished '{func.__name__}' in {time_str}")
            else:
                print(f"Finished '{func.__name__}' in {time_str}")
                
            return result
        return wrapper
    return decorator
