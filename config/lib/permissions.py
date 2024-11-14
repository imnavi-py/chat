# create by: ayoub taneh (2024-08-08)
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from config.lib.setting import APP_KEY
from config.settings import DEBUG



#region ==================== def ====================

def method_permission_map(method):
    '''Mapping HTTP methods to the corresponding permissions'''
    permission_map = {
        'GET': 'view',
        'POST': 'add',
        'PUT': 'change',
        'PATCH': 'change',
        'DELETE': 'delete',
    }
    return permission_map.get(method.upper())


def get_biz_id(request):
    return request.headers.get('bizid', None)


def get_role_id(request):
    return request.headers.get('roleid', None)


def check_user_permission(request, permission_codename, biz_id=None, role_id=None, raised=False):
    """
    Checks whether the user has the required permission for a specific action.

    This function evaluates the user's permissions based on the provided `biz_id` and `role_id`. 
    If the user is a superuser, the function immediately returns `True`, granting all permissions.

    :param request: The HTTP request object that contains user information. This should include the authenticated user and their associated permissions.
    :param permission_codename: The codename of the permission to be checked, typically formatted as `<action>_<model>`, e.g., `view_role`.
    :param biz_id: The ID of the business in which the user operates. If not provided, it will be retrieved using the `get_biz_id(request)` function.
    :param role_id: The ID of the user's role within the business. If not provided, it will be retrieved using the `get_role_id(request)` function.
    :param raised: If `True`, raises a `PermissionDenied` exception when the permission is not found. Default is `False`.
    
    :return: Returns `True` if the user has the required permission; otherwise, returns `False`. 
    If `raised=True` and the user lacks the permission, a `PermissionDenied` exception is raised.
    
    Example Usage:
    
        In view.py:
        
            1- if use for all method:
                # use from `serializer = self.get_serializer()` in another def
                class RoleView(viewsets.ModelViewSet)
                
                    def get_serializer(self, *args, **kwargs):
                        kwargs['request'] = self.request
                        return super().get_serializer(*args, **kwargs)
                    
                # in serializer:
                def __init__(self, *args, **kwargs):
                    self.request = kwargs.pop('request', None)
                    super().__init__(*args, **kwargs)
            
            2- if use for one method or def:
                # add `context={'request': request}` to serializer
                ser = serializer.RoleSerializer(instance, data=request.data, partial=True, context={'request': request})
                # or
                ser = self.get_serializer(instance, data=request.data, partial=True)
            
        
        in serializer:
        from config.lib.permissions import check_user_permission
        class RoleSerializer(serializers.ModelSerializer):            
            
            class Meta:
                model = Role
                exclude = '__all__'
            
            def update(self, instance, validated_data):
                request = self.context.get('request') or self.request
                
                if 'business' in validated_data:
                    check_user_permission(request,'change_business_field_role', raised=True)
                
                return super().update(instance, validated_data)
                
        in apps.py:
            def create_permissions(self):
                more_permissions = [
                {
                    'name': f"Can change business field from {self.name} table", 
                    # Please do not modify the following content as it is used in the following places:
                    # 1- role.serializers.RoleByFieldSerializer.update
                    'codename': f'change_business_field_{self.name}', # change_business_field_role
                    'tables': self.name
                }
            ]
            ...
    """
        
    # check SuperUser
    if request.user.is_superuser:
        return True
    
    if request is None:
        raise ValueError("Request object cannot be None! please add `context={'request': request}` to `serialiser")
    
    if biz_id is None:
        biz_id = get_biz_id(request)
        
    if role_id is None:
        role_id = get_role_id(request)
      
    if biz_id is not None and role_id is not None:
        user_permissions = request.user.user_permissions
        for biz in user_permissions:
            if biz_id in biz:
                biz_items = biz[biz_id]
                for employee in biz_items:
                    positions = employee['positions']
                    for position in positions:
                        if role_id in position['role']['id']:
                            for group in position['groups']:
                                permissions = group['group'].get('permissions', [])
                                if permissions:
                                    for permission in permissions:
                                        if permission['permission']['codename'] == permission_codename:
                                            return True
    else:
        print(f'Warning: def check_user_permission, `bizid` and `roleid` is required!')
    
    if raised:
        raise PermissionDenied()
    
    return False

#endregion



class IsAuthenticated(BasePermission):
    
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated
        )
    
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)



class IsAppKeyToken(BasePermission):
    
    
    def has_permission(self, request, view):
        token = request.COOKIES.get('token')
        if not token and DEBUG:
            token = request.headers.get('Authorization')
            
        return token == APP_KEY
    

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
      
 
 
class IsSuperUser(BasePermission):
    
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_superuser
        )
    
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
        
        
          
class IsCreator(BasePermission):
    
    
    def has_permission(self, request, view):
        print('Notice: (class IsCreator) Please use has_object_permission, has_permission is not supported')
        return False
    
    
    def has_object_permission(self, request, view, obj):
        creator_field = getattr(view, 'creator_field_name', None)
        if creator_field is None:
            print('Notice: (class IsCreator) Please send ((creator_field_name))!')
            return False
        
        creator = getattr(obj, creator_field, None)
        return creator == request.user



class IsValidMethod(BasePermission):
    
    
    def has_permission(self, request, view):
        method = method_permission_map(request.method)
        if not method:
            print(f"Warning: class `{self.__class__.__name__}`. not supported method is: {request.method}, user.id: {request.user.id}")
            return False
        return method
    
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)



class IsValidModel(BasePermission):
    
    
    def has_permission(self, request, view):
        model_name = getattr(view, 'model_name', None)
        if not model_name:
            print(f"Warning: class `{self.__class__.__name__}`. Please set `model_name` in your views")
            return False
        return model_name
    
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)



class IsBizRolePermission(BasePermission):

    
    def has_permission(self, request, view):
        # check Authenticated
        if not IsAuthenticated().has_permission(request, view):
            return False
        
        # check method and model
        model_name = IsValidModel().has_permission(request, view)
        method = IsValidMethod().has_permission(request, view)
        if model_name == False or method == False:
            print(f"Warning: class `{self.__class__.__name__}` invalid `model_name` or `method`")
            return False
    
        permission_codename = f"{method}_{model_name}"
       
        return check_user_permission(request, permission_codename)

    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)



