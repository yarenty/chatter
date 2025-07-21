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

# Monkeypatch mem0.memory.graph_memory to sanitize relationship labels before creating Cypher queries.
# This fixes CypherSyntaxError for relationship types with spaces.
try:
    import mem0.memory.graph_memory
    import logging
    import inspect
    logger = logging.getLogger(__name__)

    logger.info("Attempting to monkeypatch mem0 to fix Cypher syntax errors")
    
    # Dynamically find the class that has the method we need to patch.
    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, '_add_entities'):
            GraphMemoryClass = obj
            logger.info(f"Found class '{name}' to patch for Cypher syntax fix.")
            break

    if GraphMemoryClass:
        original_add_entities = getattr(GraphMemoryClass, '_add_entities')

        def patched_add_entities(self, entities, *args, **kwargs):
            # Sanitize relationship labels in entities before calling the original function
            if isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                        # Replace spaces with underscores, as Neo4j doesn't like spaces in rel types without backticks
                        entity["relationship"] = entity["relationship"].replace(" ", "_")
            
            # Call the original method with the sanitized entities
            return original_add_entities(self, entities, *args, **kwargs)

        setattr(GraphMemoryClass, '_add_entities', patched_add_entities)
        logger.info(f"Successfully monkeypatched {GraphMemoryClass.__name__}._add_entities")
    else:
        logger.warning("Could not find a class with method '_add_entities' to patch for Cypher syntax.")

except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to apply mem0 monkeypatch for Cypher syntax: {e}")
    pass 