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

# Monkeypatch mem0.memory.graph_memory.GraphMemory._remove_spaces_from_entities
# to handle stringified JSON bug where entities are passed as a string instead of a list of dicts.
try:
    import mem0.memory.graph_memory
    import json
    import logging
    import inspect
    logger = logging.getLogger(__name__)

    logger.info("Attempting to monkeypatch _remove_spaces_from_entities in mem0.memory.graph_memory")
    
    # Dynamically find the class that has the method we need to patch.
    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, '_remove_spaces_from_entities'):
            GraphMemoryClass = obj
            logger.info(f"Found class '{name}' to patch.")
            break

    if GraphMemoryClass:
        original_remove_spaces_from_entities = getattr(GraphMemoryClass, '_remove_spaces_from_entities')

        def patched_remove_spaces_from_entities(self, entities):
            processed_entities = []
            # If entities are a string, try to parse as JSON. This is the core of the bug fix.
            if isinstance(entities, str):
                try:
                    processed_entities = json.loads(entities)
                except json.JSONDecodeError:
                    logger.warning("Could not decode entities JSON string in monkeypatch, returning empty list.")
                    return []
            else:
                processed_entities = entities

            # Ensure we have a list to iterate over.
            if not isinstance(processed_entities, list):
                logger.warning("Entities are not a list in monkeypatch after processing, returning empty list.")
                return []

            # Safely perform the original function's logic.
            for item in processed_entities:
                if isinstance(item, dict):
                    if "source" in item and isinstance(item.get("source"), str):
                        item["source"] = item["source"].lower().replace(" ", "_")
                    if "destination" in item and isinstance(item.get("destination"), str):
                        item["destination"] = item["destination"].lower().replace(" ", "_")
            
            return processed_entities

        setattr(GraphMemoryClass, '_remove_spaces_from_entities', patched_remove_spaces_from_entities)
        logger.info(f"Successfully monkeypatched {GraphMemoryClass.__name__}._remove_spaces_from_entities")
    else:
        logger.warning("Could not find a class with method '_remove_spaces_from_entities' to patch.")

except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to apply mem0 monkeypatch for _remove_spaces_from_entities: {e}")
    pass 