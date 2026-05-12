import logging
from shared.config import config

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File Handler (Optional based on environment)
        if config.ENVIRONMENT == "production":
            try:
                fh = logging.FileHandler("app.log")
                fh.setFormatter(formatter)
                logger.addHandler(fh)
            except Exception:
                pass
                
    return logger
