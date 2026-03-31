"""Zep Rate Limiter - fixes 429 on Free plan"""
import time
import threading
import logging

logger = logging.getLogger('mirofish.rate_limiter')

class ZepRateLimiter:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.request_times = []
        self.max_requests = 5
        self.window = 60
        self.min_interval = 13.0
        self.blocked_until = None
        self.lock = threading.Lock()
        self.cache = {}
        self.cache_ttl = 300
        logger.info("ZepRateLimiter initialized: 5 req/60s, 13s spacing")
    
    def wait(self):
        with self.lock:
            now = time.time()
            if self.blocked_until and now < self.blocked_until:
                wait = self.blocked_until - now + 1
                logger.warning(f"Rate limited. Waiting {wait:.0f}s")
                time.sleep(wait)
                now = time.time()
                self.blocked_until = None
            
            self.request_times = [t for t in self.request_times if t > now - self.window]
            
            if len(self.request_times) >= self.max_requests:
                wait = self.request_times[0] + self.window - now + 1
                if wait > 0:
                    logger.info(f"Quota full. Waiting {wait:.0f}s")
                    time.sleep(wait)
                    now = time.time()
                    self.request_times = [t for t in self.request_times if t > now - self.window]
            
            if self.request_times:
                elapsed = now - self.request_times[-1]
                if elapsed < self.min_interval:
                    time.sleep(self.min_interval - elapsed)
                    now = time.time()
            
            self.request_times.append(now)
    
    def handle_429(self, retry_after=60):
        with self.lock:
            self.blocked_until = time.time() + retry_after
            self.request_times = []
        logger.warning(f"429 received. Blocked for {retry_after}s")
    
    def get_cached(self, key):
        if key in self.cache:
            data, ts = self.cache[key]
            if time.time() - ts < self.cache_ttl:
                logger.info(f"Cache HIT: {key[:50]}")
                return data
            del self.cache[key]
        return None
    
    def set_cached(self, key, data):
        self.cache[key] = (data, time.time())

rate_limiter = ZepRateLimiter()
