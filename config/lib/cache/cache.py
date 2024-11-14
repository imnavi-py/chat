from django.core.cache import cache



def set(key, value, timeout=None):
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        # send error to log and admin notification
        print(f'Cache saving error: {e}')


def get(key):
    value = None

    try:
        value = cache.get(key)
    except Exception as e:
        # send error to log and admin notification
        print(f'Cache getting error! {e}')

    return value


def delete(key):
    try:
        cache.delete(key)
    except Exception as e:
        # send error to log and admin notification
        print(f'Cache deletion error! {e}')
