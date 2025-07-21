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

# Monkeypatch mem0.memory.graph_memory to fix multiple bugs
# 1. TypeError: handle stringified JSON in _remove_spaces_from_entities
# 2. CypherSyntaxError: sanitize relationship labels in _add_entities
try:
    import mem0.memory.graph_memory
    import json
    import logging
    import inspect
    import re
    logger = logging.getLogger(__name__)

    logger.info("Attempting to apply mem0 monkeypatches...")
    
    # Dynamically find the class to patch
    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, '_add_entities') and hasattr(obj, '_remove_spaces_from_entities'):
            GraphMemoryClass = obj
            logger.info(f"Found class '{name}' to patch.")
            break

    if GraphMemoryClass:
        # ===== PATCH 1: Fix TypeError in _remove_spaces_from_entities =====
        original_remove_spaces = getattr(GraphMemoryClass, '_remove_spaces_from_entities')

        def patched_remove_spaces(self, entities):
            processed_entities = []
            if isinstance(entities, str):
                try:
                    processed_entities = json.loads(entities)
                except json.JSONDecodeError:
                    return []
            else:
                processed_entities = entities
            return original_remove_spaces(self, processed_entities)

        setattr(GraphMemoryClass, '_remove_spaces_from_entities', patched_remove_spaces)
        logger.info(f"Successfully patched {GraphMemoryClass.__name__}._remove_spaces_from_entities")

        # ===== PATCH 2: Fix CypherSyntaxError in _add_entities =====
        original_add_entities = getattr(GraphMemoryClass, '_add_entities')

        def patched_add_entities(self, entities, *args, **kwargs):
            if isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                        rel = entity["relationship"]
                        # Sanitize relationship label for Cypher:
                        # 1. Replace spaces and hyphens with underscores.
                        rel = rel.replace(" ", "_").replace("-", "_")
                        # 2. Remove all other non-alphanumeric characters (keeps letters, numbers, underscore).
                        rel = re.sub(r'[^\w]', '', rel)
                        entity["relationship"] = rel
            return original_add_entities(self, entities, *args, **kwargs)

        setattr(GraphMemoryClass, '_add_entities', patched_add_entities)
        logger.info(f"Successfully patched {GraphMemoryClass.__name__}._add_entities")
    else:
        logger.warning("Could not find a class with all required methods to patch in mem0.")

except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to apply mem0 monkeypatches: {e}")
    pass 