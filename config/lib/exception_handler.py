from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from . ApiResponse import token_and_cookie


def custom_reponse_func(error, errorCode, message='An error occurred.'):
    custom_response = {
        'status': {
            "code": errorCode,
            "message": _(message),
            "type": "fail"
        },
        'data': [],
        'error': error,
    }
    return custom_response


def custom_exception_handler(exc, context):
    # Get the request object from context
    request = context.get('request', None)

    # Get the user token if the user is authenticated
    token = None
    if request and hasattr(request.user, 'token'):
        token = request.user.token
        
    # Call the default exception handler first
    response = exception_handler(exc, context)

    # If an exception is handled by the DRF default handler, modify the response
    if response is not None:
        # print('!!! response is not None: !!!')
        if 'detail' in response.data:
            error_message = response.data['detail']
            custom_response = custom_reponse_func(error_message, response.status_code)
            response.data = custom_response
        else:
            custom_response = custom_reponse_func(response.data, response.status_code)
            response.data = custom_response
    
        if token:
            # print('!!! token: !!!')
            response = token_and_cookie(response, token)

    # Handle ValueError specifically
    elif isinstance(exc, ValueError):
        custom_response = custom_reponse_func(str(exc), status.HTTP_404_NOT_FOUND)
        return Response(custom_response, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, ValidationError):
        custom_response = custom_reponse_func(str(exc), status.HTTP_400_BAD_REQUEST)
        return Response(custom_response, status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(exc, AuthenticationFailed):
        custom_response = custom_reponse_func(str(exc), status.HTTP_401_UNAUTHORIZED, 'Authentication failed')
        return Response(custom_response, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, NotAuthenticated):
        custom_response = custom_reponse_func(str(exc), status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, 'Not authenticated')
        return Response(custom_response, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

    elif isinstance(exc, PermissionDenied):
        custom_response = custom_reponse_func(str(exc), status.HTTP_403_FORBIDDEN, 'Permission denied')
        return Response(custom_response, status=status.HTTP_403_FORBIDDEN)

    elif isinstance(exc, json.JSONDecodeError):
        custom_response = custom_reponse_func(str(exc), status.HTTP_400_BAD_REQUEST, 'Invalid Inputs')
        return Response(custom_response, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     custom_response = custom_reponse_func(str(exc),status.HTTP_500_INTERNAL_SERVER_ERROR,'An unexpected error occurred.')
    #     return Response(custom_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return response