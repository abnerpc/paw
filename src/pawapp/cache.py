"""Module to access and save data through the Django cache system."""
import pickle
from django.core.cache import cache


def get_value(key):
    """Get value from cache using pickle.

    Args:
        key (str): Cache key.

    Returns:
        obj: Cached object.

    """
    data = cache.get(key)
    if data:
        return pickle.loads(data)


def set_value(key, data):
    """Set value in the cache using pickle.

    Args:
        key (str): Cache key.
        data (obj): Object to be saved.

    """
    if not key or not data:
        return

    cache.set(key, pickle.dumps(data))
