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
            logger.info("Executing patched _add_entities...")
            if isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                        original_rel = entity["relationship"]
                        
                        # Build a sanitized relationship string character by character
                        sanitized_chars = []
                        for char in original_rel:
                            if char.isalnum():
                                sanitized_chars.append(char)
                            elif char.isspace() or char == '-':
                                sanitized_chars.append('_')
                        
                        final_rel = "".join(sanitized_chars)

                        # If sanitization results in an empty string, use a default
                        if not final_rel:
                            final_rel = "RELATED_TO"
                        
                        logger.info(f"Sanitizing relationship: '{original_rel}' -> '{final_rel}'")
                        entity["relationship"] = final_rel
                        
            return original_add_entities(self, entities, *args, **kwargs)

        setattr(GraphMemoryClass, '_add_entities', patched_add_entities)
        logger.info(f"Successfully patched {GraphMemoryClass.__name__}._add_entities")
    else:
        logger.warning("Could not find a class with all required methods to patch in mem0.")

except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to apply mem0 monkeypatches: {e}")
    pass 

# === Additional patch: Sanitize relationships in both add and _add_entities ===
try:
    import mem0.memory.graph_memory
    import inspect
    import logging
    logger = logging.getLogger(__name__)

    def sanitize_relationships(entities):
        changed = False
        if isinstance(entities, list):
            for entity in entities:
                if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                    original_rel = entity["relationship"]
                    sanitized_chars = []
                    for char in original_rel:
                        if char.isalnum():
                            sanitized_chars.append(char)
                        elif char.isspace() or char == '-':
                            sanitized_chars.append('_')
                    final_rel = "".join(sanitized_chars)
                    if not final_rel:
                        final_rel = "RELATED_TO"
                    if final_rel != original_rel:
                        logger.info(f"Sanitizing relationship: '{original_rel}' -> '{final_rel}'")
                    entity["relationship"] = final_rel
                    changed = True
        return entities

    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, 'add'):
            GraphMemoryClass = obj
            logger.info(f"[extra patch] Found class '{name}' to patch for add/_add_entities.")
            break

    if GraphMemoryClass:
        # Patch add
        orig_add = getattr(GraphMemoryClass, 'add')
        def patched_add(self, data, *args, **kwargs):
            if isinstance(data, list):
                sanitize_relationships(data)
            elif isinstance(data, dict) and "entities" in data:
                sanitize_relationships(data["entities"])
            print("CALLED: add (patched)")
            return orig_add(self, data, *args, **kwargs)
        setattr(GraphMemoryClass, 'add', patched_add)

        # Patch _add_entities if it exists
        if hasattr(GraphMemoryClass, '_add_entities'):
            orig_add_entities = getattr(GraphMemoryClass, '_add_entities')
            def patched_add_entities(self, entities, *args, **kwargs):
                sanitize_relationships(entities)
                print("CALLED: _add_entities (patched)")
                return orig_add_entities(self, entities, *args, **kwargs)
            setattr(GraphMemoryClass, '_add_entities', patched_add_entities)

        logger.info(f"[extra patch] Patched add and _add_entities in {GraphMemoryClass.__name__}")
    else:
        logger.warning("[extra patch] Could not find a class with 'add' to patch in mem0.memory.graph_memory.")
except Exception as e:
    logger.warning(f"[extra patch] Failed to apply add/_add_entities patch: {e}") 

# === Additional patch: Sanitize relationships in all search/retrieve methods ===
try:
    import mem0.memory.graph_memory
    import inspect
    import logging
    logger = logging.getLogger(__name__)

    def sanitize_relationships(entities):
        changed = False
        if isinstance(entities, list):
            for entity in entities:
                if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                    original_rel = entity["relationship"]
                    sanitized_chars = []
                    for char in original_rel:
                        if char.isalnum():
                            sanitized_chars.append(char)
                        elif char.isspace() or char == '-':
                            sanitized_chars.append('_')
                    final_rel = "".join(sanitized_chars)
                    if not final_rel:
                        final_rel = "RELATED_TO"
                    if final_rel != original_rel:
                        logger.info(f"Sanitizing relationship: '{original_rel}' -> '{final_rel}' (search/retrieve)")
                    entity["relationship"] = final_rel
                    changed = True
        return entities

    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, 'add'):
            GraphMemoryClass = obj
            logger.info(f"[extra patch] Found class '{name}' to patch for search/retrieve.")
            break

    if GraphMemoryClass:
        for method_name, method in inspect.getmembers(GraphMemoryClass, predicate=inspect.isfunction):
            if method_name.startswith('search') or method_name.startswith('retrieve'):
                orig_method = getattr(GraphMemoryClass, method_name)
                def make_patched(orig_func, method_name):
                    def wrapper(self, *args, **kwargs):
                        # Try to sanitize relationships in all list/dict args
                        for arg in args:
                            if isinstance(arg, list):
                                sanitize_relationships(arg)
                            elif isinstance(arg, dict) and "entities" in arg:
                                sanitize_relationships(arg["entities"])
                        for k, v in kwargs.items():
                            if isinstance(v, list):
                                sanitize_relationships(v)
                            elif isinstance(v, dict) and "entities" in v:
                                sanitize_relationships(v["entities"])
                        print(f"CALLED: {method_name} (patched)")
                        return orig_func(self, *args, **kwargs)
                    return wrapper
                setattr(GraphMemoryClass, method_name, make_patched(orig_method, method_name))
        logger.info(f"[extra patch] Patched all search/retrieve methods in {GraphMemoryClass.__name__}")
    else:
        logger.warning("[extra patch] Could not find a class with 'add' to patch for search/retrieve in mem0.memory.graph_memory.")
except Exception as e:
    logger.warning(f"[extra patch] Failed to apply search/retrieve patch: {e}") 

# === Patch: Sanitize relationships in _delete_entities and query ===
try:
    import mem0.memory.graph_memory
    import inspect
    import logging
    logger = logging.getLogger(__name__)

    def sanitize_relationships(entities):
        if isinstance(entities, list):
            for entity in entities:
                if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                    original_rel = entity["relationship"]
                    sanitized_chars = []
                    for char in original_rel:
                        if char.isalnum():
                            sanitized_chars.append(char)
                        elif char.isspace() or char == '-':
                            sanitized_chars.append('_')
                    final_rel = "".join(sanitized_chars)
                    if not final_rel:
                        final_rel = "RELATED_TO"
                    if final_rel != original_rel:
                        logger.info(f"Sanitizing relationship: '{original_rel}' -> '{final_rel}' (_delete_entities/query)")
                    entity["relationship"] = final_rel
        return entities

    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and (hasattr(obj, '_delete_entities') or hasattr(obj, 'query')):
            GraphMemoryClass = obj
            logger.info(f"[extra patch] Found class '{name}' to patch for _delete_entities/query.")
            break

    if GraphMemoryClass:
        # Patch _delete_entities
        if hasattr(GraphMemoryClass, '_delete_entities'):
            orig_delete_entities = getattr(GraphMemoryClass, '_delete_entities')
            def patched_delete_entities(self, entities, *args, **kwargs):
                sanitize_relationships(entities)
                print("CALLED: _delete_entities (patched)")
                return orig_delete_entities(self, entities, *args, **kwargs)
            setattr(GraphMemoryClass, '_delete_entities', patched_delete_entities)
            logger.info(f"[extra patch] Patched _delete_entities in {GraphMemoryClass.__name__}")
        # Patch query
        if hasattr(GraphMemoryClass, 'query'):
            orig_query = getattr(GraphMemoryClass, 'query')
            def patched_query(self, *args, **kwargs):
                # Try to sanitize relationships in all list/dict args
                for arg in args:
                    if isinstance(arg, list):
                        sanitize_relationships(arg)
                    elif isinstance(arg, dict) and "entities" in arg:
                        sanitize_relationships(arg["entities"])
                for k, v in kwargs.items():
                    if isinstance(v, list):
                        sanitize_relationships(v)
                    elif isinstance(v, dict) and "entities" in v:
                        sanitize_relationships(v["entities"])
                print("CALLED: query (patched)")
                return orig_query(self, *args, **kwargs)
            setattr(GraphMemoryClass, 'query', patched_query)
            logger.info(f"[extra patch] Patched query in {GraphMemoryClass.__name__}")
    else:
        logger.warning("[extra patch] Could not find a class with '_delete_entities' or 'query' to patch in mem0.memory.graph_memory.")
except Exception as e:
    logger.warning(f"[extra patch] Failed to apply _delete_entities/query patch: {e}") 

# === Patch: Sanitize relationships in all graph.query methods used in mem0.memory.graph_memory ===
try:
    import mem0.memory.graph_memory
    import inspect
    import logging
    logger = logging.getLogger(__name__)

    def sanitize_relationships(entities):
        if isinstance(entities, list):
            for entity in entities:
                if isinstance(entity, dict) and "relationship" in entity and isinstance(entity.get("relationship"), str):
                    original_rel = entity["relationship"]
                    sanitized_chars = []
                    for char in original_rel:
                        if char.isalnum():
                            sanitized_chars.append(char)
                        elif char.isspace() or char == '-':
                            sanitized_chars.append('_')
                    final_rel = "".join(sanitized_chars)
                    if not final_rel:
                        final_rel = "RELATED_TO"
                    if final_rel != original_rel:
                        logger.info(f"Sanitizing relationship: '{original_rel}' -> '{final_rel}' (graph.query)")
                    entity["relationship"] = final_rel
        return entities

    # Patch all classes in mem0.memory.graph_memory that have a 'query' method
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, 'query'):
            orig_query = getattr(obj, 'query')
            def make_patched_query(orig_func, class_name):
                def patched_query(self, *args, **kwargs):
                    # Try to sanitize relationships in all list/dict args
                    for arg in args:
                        if isinstance(arg, list):
                            sanitize_relationships(arg)
                        elif isinstance(arg, dict) and "entities" in arg:
                            sanitize_relationships(arg["entities"])
                    for k, v in kwargs.items():
                        if isinstance(v, list):
                            sanitize_relationships(v)
                        elif isinstance(v, dict) and "entities" in v:
                            sanitize_relationships(v["entities"])
                    print(f"CALLED: {class_name}.query (patched)")
                    return orig_func(self, *args, **kwargs)
                return patched_query
            setattr(obj, 'query', make_patched_query(orig_query, name))
            logger.info(f"[extra patch] Patched query in {name}")
except Exception as e:
    logger.warning(f"[extra patch] Failed to apply graph.query patch: {e}") 

# === Patch: Ensure filters['user_id'] always exists in _retrieve_nodes_from_data ===
try:
    import mem0.memory.graph_memory
    import inspect
    import logging
    logger = logging.getLogger(__name__)

    GraphMemoryClass = None
    for name, obj in inspect.getmembers(mem0.memory.graph_memory):
        if inspect.isclass(obj) and hasattr(obj, '_retrieve_nodes_from_data'):
            GraphMemoryClass = obj
            logger.info(f"[extra patch] Found class '{name}' to patch for _retrieve_nodes_from_data.")
            break

    if GraphMemoryClass:
        orig_method = getattr(GraphMemoryClass, '_retrieve_nodes_from_data')
        def patched_method(self, *args, **kwargs):
            # Find filters argument (usually second positional or in kwargs)
            filters = None
            if len(args) > 1 and isinstance(args[1], dict):
                filters = args[1]
            elif 'filters' in kwargs and isinstance(kwargs['filters'], dict):
                filters = kwargs['filters']
            if filters is not None and 'user_id' not in filters:
                filters['user_id'] = 'user'
                logger.info("[extra patch] Added missing 'user_id' to filters in _retrieve_nodes_from_data")
            return orig_method(self, *args, **kwargs)
        setattr(GraphMemoryClass, '_retrieve_nodes_from_data', patched_method)
        logger.info(f"[extra patch] Patched _retrieve_nodes_from_data in {GraphMemoryClass.__name__}")
    else:
        logger.warning("[extra patch] Could not find a class with '_retrieve_nodes_from_data' to patch in mem0.memory.graph_memory.")
except Exception as e:
    logger.warning(f"[extra patch] Failed to apply _retrieve_nodes_from_data patch: {e}") 