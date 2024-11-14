from config.lib.setting import AUTH_TOKEN_VALIDITY
from . cache import cache


def _generate_key(user_id):
    return f"user_permissions_{user_id}"


def get(user_id):
    key = _generate_key(user_id)
    return( cache.get(key=key) )


def set(user_permissions, user_id):
    key = _generate_key(user_id)
    cache.set(key, user_permissions, AUTH_TOKEN_VALIDITY)


def delete(user_id):
    key = _generate_key(user_id)
    cache.delete(key)


# ========================================================
    
def _generate_permisions_key():
    return 'permissions'


def get_permisions():
    key = _generate_permisions_key()
    return( cache.get(key=key) )


def set_permisions(permissions):
    key = _generate_permisions_key()
    # print('!!! set_permisions() key: ', key)
    # print('!!! set_permisions(): ',permissions)
    cache.set(key, permissions)


def get_and_set_permisions():
    '''
        get permissions from module url and save in cache
    '''
    permissions = permissions().get_all_permissions()
    set_permisions(permissions)