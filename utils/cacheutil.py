from cachetools import TTLCache

GLOBAL_CACHE = TTLCache(10000, 120)


def get_from_global_cache(key):
    return GLOBAL_CACHE.get(key)


def set_in_global_cache(key, value):
    GLOBAL_CACHE[key] = value


def delete_from_global_cache(key):
    GLOBAL_CACHE.pop(key, None)