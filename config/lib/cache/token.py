import random, string, uuid, json
from config.lib.setting import AUTH_TOKEN_VALIDITY, TOKEN_UPDATE_TIME, TOKEN_REFRESH, APP_KEY
from config.lib.utils import safe_to_dict
from config.lib.api import AsyncUserAPI
from config.lib.uuid import UUIDEncoder
from types import SimpleNamespace
from datetime import datetime
from . import cache, permission

USER_PREFIX = 'user_'


def _generate_token_key(token):
    '''
    token: "sdfgsdgkjuhiuhdf8794yhrthweofuy97whfhwe97ry943uhf"
    '''
    return f"{USER_PREFIX}{token}"



def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=67)) + str(uuid.uuid4().hex)



def get_token(token):
    '''
    token: "sdfgsdgkjuhiuhdf8794yhrthweofuy97whfhwe97ry943uhf"
    '''
    key = _generate_token_key(token)
    user_js = cache.get(key=key)
    if user_js is None:
        return None

    user_dic = json.loads(user_js)
    
    if 'id' in user_dic:
        user_dic['id'] = uuid.UUID(user_dic['id'])
        
    return SimpleNamespace(**user_dic)



def set_token(token, user):
    '''
        token: string
        user: object
    '''
    
    key = _generate_token_key(token)
    user_data = safe_to_dict(user)
    
    # Convert datetime fields to strings
    for field, value in user_data.items():
        
        if isinstance(value, datetime):
            user_data[field] = value.isoformat()
    
    # received user permissions history
    if not user_data.get('received_user_permissions', False):
        # print('!!! received user permissions history: False')
        user_data['received_user_permissions'] = False
        
    # get permissions 
    if user_data['received_user_permissions'] == False:
        # print('!!! get permissions with AsyncUserAPI()')
        user_data['user_permissions'] = AsyncUserAPI().get_user_details(user.pk, APP_KEY, ['permissions']) ['permissions']
        user_data['received_user_permissions'] = True
        
    user_data['avatar_url'] = getattr(user, 'avatar_url', None)
    user_data['token'] = token
    user_data['is_authenticated'] = True
    user_data['password'] = ''
    user_data['pk'] = user.pk
    user_data['id'] = user.pk
    # print('!!!!1111 user_data: ', user_data)
    cache.set(key, json.dumps(user_data, cls=UUIDEncoder), AUTH_TOKEN_VALIDITY)



def del_token(token, user_id=None):
    '''
    token: "sdfgsdgkjuhiuhdf8794yhrthweofuy97whfhwe97ry943uhf"
    '''
    if user_id:
        cache.delete(
            _generate_last_token_key(user_id)
        )

    key = _generate_token_key(token)
    cache.delete(key)



# --------------------------------------------------------------

def _generate_last_token_key(user_id):
    return f'token_{user_id}'


def get_last_token(user_id):
    key = _generate_last_token_key(user_id)
    return cache.get(key=key)


def set_last_token(user_id, token):
    key = _generate_last_token_key(user_id)
    cache.set(key, token, AUTH_TOKEN_VALIDITY)



# ===============================================================

def token_setting_check(user, token):
    '''
        Checked:
            setting.TOKEN_REFRESH
            setting.TOKEN_UPDATE_TIME
    '''
    reset_token = False
    
    # token refresh on every request
    if TOKEN_REFRESH:
        reset_token = True
        
        #delete last token
        del_token(token, user.id)
        
        # generate new token
        token = generate_token()
    
    # Rewrite to update time
    if TOKEN_UPDATE_TIME:
        reset_token = True
        
    if reset_token:
        set_token(token, user)
        set_last_token(user.id, token)
        user = get_token(token)
        
    return user, token
