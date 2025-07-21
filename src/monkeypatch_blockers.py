import logging
logger = logging.getLogger(__name__)

# Dummy response class for blocked requests (always OK)
class DummyResponse:
    status_code = 200
    text = "OK"
    content = b"OK"
    def json(self): return {"success": True}

# Monkeypatch httpx to block requests to OpenAI, PostHog, and known IPs
try:
    import httpx
    original_request = httpx.Client.request
    def block_external_requests(self, method, url, *args, **kwargs):
        if ("openai.com" in url or "posthog.com" in url or "18.204.119.245" in url or "174.129.227.208" in url):
            return DummyResponse()
        return original_request(self, method, url, *args, **kwargs)
    httpx.Client.request = block_external_requests
except ImportError:
    pass

# Monkeypatch requests to block requests to OpenAI, PostHog, and known IPs
try:
    import requests
    _original_request = requests.sessions.Session.request
    def block_requests(self, method, url, *args, **kwargs):
        if ("openai.com" in url or "posthog.com" in url or "18.204.119.245" in url or "174.129.227.208" in url):
            return DummyResponse()
        return _original_request(self, method, url, *args, **kwargs)
    requests.sessions.Session.request = block_requests
except ImportError:
    pass

# Monkeypatch urllib3 to block requests to OpenAI, PostHog, and known IPs
try:
    import urllib3
    _original_urlopen = urllib3.PoolManager.urlopen
    def block_urllib3(self, method, url, *args, **kwargs):
        if ("openai.com" in url or "posthog.com" in url or "18.204.119.245" in url or "174.129.227.208" in url):
            return DummyResponse()
        return _original_urlopen(self, method, url, *args, **kwargs)
    urllib3.PoolManager.urlopen = block_urllib3
except ImportError:
    pass 

# Monkeypatch mem0.graph_memory.extract_entities to ensure entities is always a list, not a string
try:
    import mem0.memory.graph_memory as graph_memory
    import json
    orig_extract_entities = getattr(graph_memory, 'extract_entities', None)
    if orig_extract_entities:
        def safe_extract_entities(*args, **kwargs):
            result = orig_extract_entities(*args, **kwargs)
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except Exception:
                    pass
            return result
        graph_memory.extract_entities = safe_extract_entities
except ImportError:
    pass 