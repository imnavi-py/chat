# import json
# from channels.auth import AuthMiddlewareStack
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import AnonymousUser
# from rest_framework.authtoken.models import Token
# from urllib.parse import parse_qs

# class TokenAuthMiddleware:
#     """
#     Middleware for authenticating WebSocket connections using token-based authentication.
#     """

#     def __init__(self, inner):
#         self.inner = inner

#     async def __call__(self, scope, receive, send):
#         # Get the token from the query parameters
#         query_string = parse_qs(scope['query_string'].decode())
#         token = query_string.get('token', [None])[0]

#         # Check if token is provided
#         if token:
#             user = await self.get_user_from_token(token)
#             if user:
#                 scope['user'] = user
#             else:
#                 scope['user'] = AnonymousUser()
#         else:
#             scope['user'] = AnonymousUser()

#         # Call the inner application
#         return await self.inner(scope, receive, send)

#     @database_sync_to_async
#     def get_user_from_token(self, token):
#         try:
#             token_instance = Token.objects.get(key=token)
#             return token_instance.user
#         except Token.DoesNotExist:
#             return None

# def TokenAuthMiddlewareStack(inner):
#     return TokenAuthMiddleware(AuthMiddlewareStack(inner))
