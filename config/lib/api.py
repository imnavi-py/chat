from asgiref.sync import async_to_sync
from config.lib.setting import API, APP_KEY
import requests, asyncio, httpx


class permissions():
    
    
    def create_permissions(permissions):
        response = requests.post(
            API['permission_url'],
            json={API['permission_var']: permissions},
            headers={'Content-Type': 'application/json'},
            cookies={'token': APP_KEY}
        )
        
        # if response.status_code == 200:
        #     return True
    
    
    def get_all_permissions():
        
        response = requests.get(
            f"{API['permission_url']}?page_size=0",
            headers={'Content-Type': 'application/json'},
            cookies={'token': APP_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['results']
        else:
            print(f"Error `def get_all_permissions` StatusCode: {response.status_code}")
            return None
     

    def save_permissions_after_migration(self, name, more_permissions, is_hcm=False, set_default_permissions=True):
        # try:
        permissions_data = []
        if set_default_permissions == True:
            permissions_data = [
                {
                    'name': f'Can view data in {name} table', 
                    'codename': f'view_{name}', 
                    'tables': name
                },
                {
                    'name': f'Can add data to {name} table', 
                    'codename': f'add_{name}', 
                    'tables': name
                },
                {
                    'name': f'Can change data in {name} table', 
                    'codename': f'change_{name}', 
                    'tables': name
                },
                {
                    'name': f'Can delete from {name} table', 
                    'codename': f'delete_{name}', 
                    'tables': name
                },
            ]
            
        permissions_data = permissions_data + more_permissions

        # print(f"Notices: ---> Trying to save table permissions `{name}`")
        if is_hcm:
            from permission.views import save_default_permissions
            save_default_permissions(permissions_data)
        else:
            permissions.create_permissions(permissions_data)
    
        # except Exception as e:
        #     print(f"Warning: ---> Error in save permissions `{name}`: {str(e)}")



def _get_nested_value(dictionary, keys):
    for key in keys:
        dictionary = dictionary.get(key, {})
    return dictionary


def _set_nested_value(dictionary, keys, value):
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, {})
    dictionary[keys[-1]] = value


def getting_info(url, variable, data_list, field_name, token):
    
    user_ids_list = list(set([_get_nested_value(item, field_name) for item in data_list]))
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        url,
        json={variable: user_ids_list},
        headers=headers,
        cookies={'token': token}
    )
    
    if response.status_code == 200:
        users_info = response.json().get('data', [])
        user_info_map = {info['id']: info for info in users_info}
        for item in data_list:
            user_id = _get_nested_value(item, field_name)
            if user_id in user_info_map:
                _set_nested_value(item, field_name, user_info_map[user_id])
    else:
        print(f"lib.api.getting_info: {response.status_code}")
        
    return data_list

def getting_info_by_headers(url, variable, data_list, field_name, bizid, roleid, token):
    user_ids_list = list(set([_get_nested_value(item, field_name) for item in data_list]))

    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
        'bizid': bizid,
        'roleid': roleid
    }

    print("headers", headers)

    response = requests.post(
        url,
        json={variable: user_ids_list},
        headers=headers,
        cookies={'token': token}
    )

    if response.status_code == 200:
        print(f" success --> lib.api.getting_info: {response.status_code}")
        users_info = response.json().get('data', [])
        user_info_map = {info['id']: info for info in users_info}
        # print("user_info_map", user_info_map)
        # print("data_list", data_list)
        for item in data_list:
            user_id = _get_nested_value(item, field_name)
            if user_id in user_info_map:
                _set_nested_value(item, field_name, user_info_map[user_id])
    else:
        print(f" error --> lib.api.getting_info: {response.status_code}")

    return data_list

class get_info():
    
    
    def users(data_list, field_name =['user'], token=None):
        '''
            Use in def retrieve(...)
                ...
                data = get_info.users( [serializer.data] , request.user.token)
                ### or
                data = get_info.users([serializer.data], ['owner'], request.user.token)
                ### or
                data = get_info.users([serializer.data], ['owner', 'user'], request.user.token)

            Use in def list(...)
                ...
                data = get_info.users(serializer.data, token=request.user.token)
                ### or
                data = get_info.users(serializer.data, ['owner'])
                ### or
                data = get_info.users(serializer.data, ['owner', 'user'])
            Use for one user:
                    data = {"user":str(position.employee.user)}
                    print(api.get_info.users([data]))
        '''

        
        return getting_info(API['user_url'], API['user_var'], data_list, field_name, token)


    def bizs(data_list, field_name =['biz'], token=None):
        '''
            Use in def retrieve(...)
                ...
                biz = get_info.bizs([{'biz': str(business)}], token=APP_KEY)
                data = get_info.users( [serializer.data] , request.user.token)
                ### or
                data = get_info.users([serializer.data], ['biz'], request.user.token)
                ### or
                data = get_info.users([serializer.data], ['biz', 'business'], request.user.token)

            Use in def list(...)
                ...
                data = get_info.users(serializer.data, request.user.token)
                ### or
                data = get_info.users(serializer.data, ['biz'], request.user.token)
                ### or
                data = get_info.users(serializer.data, ['biz', 'business'], request.user.token)
        '''
            
        return getting_info(API['biz_url'], API['biz_var'], data_list, field_name, token)

    def positions(data_list, biz_id, roleid, field_name=['position'],token=None):
        '''
            Use in def retrieve(...)
                ...
                biz = get_info.positions([{'biz': str(business)}], token=APP_KEY)
                data = get_info.positions( [serializer.data] , request.user.token)
                ### or
                data = get_info.positions([serializer.data], ['biz'], request.user.token)
                ### or
                data = get_info.positions([serializer.data], ['biz', 'business'], request.user.token)

            Use in def list(...)
                ...
                data = get_info.positions(serializer.data, request.user.token)
                ### or
                data = get_info.positions(serializer.data, ['biz'], request.user.token)
                ### or
                data = get_info.positions(serializer.data, ['biz', 'business'], request.user.token)
        '''

        return getting_info_by_headers(API['position_url'], API['position_var'], data_list, field_name, biz_id, roleid,token)

class exists():
    
    
    def user(user_id, token=APP_KEY):
        '''
        Check if a specific user ID exists in the user summary by using the get_info function.

        :param user_id: The user ID to check.
        :param token: Optional authorization token. If not provided, a default token is used.
        :return: True if the user ID exists, False otherwise.
        '''

        user_list = [{ 'user': str(user_id) }]
        result = getting_info(API['user_url'], API['user_var'], user_list, ['user'], token)
        if isinstance(result[0]['user'], dict):
            return True
        return False

    def position(position_id, requester_business_id, requester_role_id, token):
        '''
        Check if a specific user ID exists in the user summary by using the get_info function.

        :param position_id: The user ID to check.
        :param token: Required authorization token.
        :param requester_business_id: Required business ID.
        :param requester_role_id: Required role ID.
        :return: True if the user ID exists, False otherwise.
        '''

        position_list = [{'position': str(position_id)}]
        # def getting_info_by_headers(url, variable, data_list, field_name, bizid, roleid, token):
        result =getting_info_by_headers(API['position_url'], API['position_var'], position_list, ['position'], requester_business_id, requester_role_id, token)
        print("position_info is:", result)
        if isinstance(result[0], dict):
            return True
        return False


# ===================================================================

class AsyncUserAPI:


    async def get_business(self, user_id, token):

        try:
            cookies = {
                'token': token
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    API['biz_url'], 
                    cookies=cookies
                )

            if response.status_code == 200:
                data = response.json()['data']['results']
                print(f'user: {user_id} business saved in cache')
                return data
            else:
                print(f'Error in receiving business by API: status={response.status_code}')
                return []

        except httpx.RequestError as e:
            print(f'Error related to API: {str(e)}')
            return None


    async def get_permissions(self, user_id, token):
        try:
            cookies = {
                'token': token
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API['user_permission_url']}?{API['user_permission_var']}={user_id}", 
                    cookies=cookies
                )

            if response.status_code == 200:
                data = response.json()['data']
                # print(f'user: {user_id} permissions saved in cache')
                return data
            else:
                print(f'Error in receiving permissions by API: status={response.status_code}')
                return []

        except httpx.RequestError as e:
            print(f'Error related to API: {str(e)}')
            return None


    async def _async_get(self, user_id, token, funcs_to_run=None):
        # If no function is specified, all functions are executed
        if funcs_to_run is None:
            funcs_to_run = ['business', 'permissions']

        tasks = []
        if 'business' in funcs_to_run:
            tasks.append(self.get_business(user_id, token))

        if 'permissions' in funcs_to_run:
            tasks.append(self.get_permissions(user_id, token))

        # Concurrent execution of selected asynchronous functions and capture their results
        results = await asyncio.gather(*tasks)

        # Creating a dictionary of results based on the implemented functions
        response = {}
        if 'business' in funcs_to_run:
            response['business'] = results[0]

        if 'permissions' in funcs_to_run:
            response['permissions'] = results[-1]

        return response


    def get_user_details(self, user_id, token, functions=None):
        '''
            Functions list:
                ['business', 'permissions']
            
            example:
                # Run all functions
                AsyncUserAPI.get_user_details(user_id, token)
                
                # run only selected functions
                AsyncUserAPI.get_user_details(user_id, token, ['permissions'])
        '''
        
        return async_to_sync(self._async_get)(user_id, token, functions)


    async def get_user_employees(self, bizid, roleid, token, functions=None):
        try:
            cookies = {
                'token': token
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': token,
                'bizid': bizid,
                'roleid': roleid
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API['user_employee_url']}",
                    cookies=cookies,
                    ** headers
                )

            if response.status_code == 200:
                data = response.json()['data']
                # print(f'user: {user_id} permissions saved in cache')
                return data
            else:
                print(f'Error in receiving employees by API: status={response.status_code}')
                return []

        except httpx.RequestError as e:
            print(f'Error related to API: {str(e)}')
            return None

