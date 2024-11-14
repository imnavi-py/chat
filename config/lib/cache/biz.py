from config.settings import AUTH_TOKEN_VALIDITY
from . cache import cache


def _generate_key(user_id):
    return f"biz_{user_id}"


def get(user_id):
    key = _generate_key(user_id)
    return( cache.get(key=key) )


def set(biz, user_id):
    key = _generate_key(user_id)
    cache.set(key, biz, AUTH_TOKEN_VALIDITY)


def delete(user_id):
    key = _generate_key(user_id)
    cache.delete(key)
