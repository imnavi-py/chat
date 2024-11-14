from django.core.cache import cache
from . import token
import json, threading



def _fetch_and_process(users, groups, roles):
    keys = cache.iter_keys(f"{token.USER_PREFIX}*")
    x = 0
    for key in keys:
        print(x)
        x = x + 1
        try:
            token_key = key.removeprefix(token.USER_PREFIX)
            user_data = token.get_token(token_key)
            if user_data is None:
                continue
            
            user_id = user_data.id
            
            if user_id in users:
                print(f"successfuly delete token for user_id: {user_id}")
                token.del_token(token_key, user_id)
                continue
            
            user_permissions = user_data.user_permissions
            for biz in user_permissions:
                for employees in biz.values():
                    for employee in employees:
                        positions = employee['positions']
                        for position in positions:
                            role_id = position['role']['id']
                            if role_id in roles:
                                print(f"Matching role found: {role_id}")
                                token.del_token(token_key, user_id)
                                continue
                            for group_pos in position['groups']:
                                group_id = group_pos['id']
                                if group_id in groups: 
                                    print(f"Matching group found: {group_id}")
                                    token.del_token(token_key, user_id)
                                    continue
            
        except json.JSONDecodeError:
            print(f"Failed to decode JSON for key: {key}")
        except Exception as e:
            print(f"Error processing key {key}: {e}")



def remove(users=[], groups=[], roles=[]):
    """
    This function deletes the key from Redis keys (online users), if it is included with `users' or `groups` or `roles` the key passed to it.
    
    Args:
        users  (list, optional): _description_. Defaults to [].
        groups (list, optional): _description_. Defaults to [].
        roles  (list, optional): _description_. Defaults to [].
    
    Example:
    ```
        from config.lib.cache.user_permissions import remove
        remove(
            users=[request.user.id],
            roles=["af5d5236-da03-4ff9-9dcd-7c96f297da9d"],
            groups=[38]
        )
    ```
    """
    threading.Thread(target=_fetch_and_process, args=(users, groups, roles)).start()
