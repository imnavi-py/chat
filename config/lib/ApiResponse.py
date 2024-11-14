from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from config.lib.setting import AUTH_TOKEN_VALIDITY


def token_and_cookie(response, token):
    
    # print('ApiResponse token: ', token)
    
    # set token in cookie
    expires_at = datetime.now() + timedelta(seconds=AUTH_TOKEN_VALIDITY)
    response.set_cookie(
        key='token',
        value=token,
        httponly=True, # Set HttpOnly to prevent access from JavaScript
        secure=True, # Set Secure to send only over HTTPS
        samesite='None', # Set SameSite to prevent CSRF attacks
        # max_age=604800,
        expires=expires_at,
        domain='.nargil.co'
    )
    
    return response


class ApiResponse:

    def success(self, message='', data=[], set_cookie=True, token=None):
        '''
            example:
                ApiResponse.success(self, set_cookie=False)
                ApiResponse.success(self, token=request.user.token)
                ApiResponse.success(self, data=response, token=request.user.token)
                ApiResponse.success(self, 'it is a message', response, token=request.user.token)
                ApiResponse.success(self, 'it is a message', response, False, token)
        '''
        response = {
            'status': {
                "code": status.HTTP_200_OK,
                "message": message,
                "type": "success"
            },
            'data':  data,
            'error': [],
        }
        response = Response(response, status=status.HTTP_200_OK)
        
        if set_cookie:
            response = token_and_cookie(response, token)
        
        print('---------- END success ----------')
        return response 


    def error(self, message='', errorMessages=[], errorStatus=status.HTTP_400_BAD_REQUEST, set_cookie=True, token=None):
        '''
            example:
                ApiResponse.error(self, set_cookie=False)
                ApiResponse.error(self, token=request.user.token)
                ApiResponse.error(self, errorMessages=serializer.errors, token=request.user.token)
                ApiResponse.error(self, 'it is a message', serializer.errors, token=request.user.token)
                ApiResponse.error(self, 'it is a message', serializer.errors, False, token)
        '''
        response = {
            'status': {
                "code": errorStatus,
                "message": message,
                "type": "fail"
            },
            'data': [],
            'error': errorMessages,
        }

        response = Response(response,status=errorStatus)

        if set_cookie:
            response = token_and_cookie(response, token)
            
        print('---------- END error ----------')
        print()
        return response
            