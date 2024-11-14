from rest_framework.authentication import TokenAuthentication as DefaultTokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
from config.lib.cache import token as cache_token
from config.lib.setting import APP_KEY
from config.settings import DEBUG



class TokenAuthentication(DefaultTokenAuthentication):
    
    def authenticate_credentials(self, token):
        user = cache_token.get_token(token)
        
        if not user:
            raise AuthenticationFailed(_('Invalid token.'))
        
        # check user is active
        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))
        
        user, token = cache_token.token_setting_check(user, token)
        
        return (user, token)


    def authenticate(self, request):
        print()
        print('---------- start ----------')
        
        token = None
                
        if DEBUG :
            token = request.headers.get('Authorization')
            print('authenticate, headers.token: ', token)
            
        if not token:
            token = request.COOKIES.get('token')
            print('authenticate, cookies.token: ', token)
        
        if not token:
            return None

        print(f"bizid : {request.headers.get('bizid')}")
        print(f"roleid: {request.headers.get('roleid')}")
        
        if token == APP_KEY:
            print('APP_KEY matched. Allowing as anonymous user.')
            anonymous_user = AnonymousUser()
            anonymous_user.token = token
            return (anonymous_user, token)
        
        return self.authenticate_credentials(token)

