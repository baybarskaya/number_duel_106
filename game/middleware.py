from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs


@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        if token:
            try:
                UntypedToken(token)
                
                decoded_data = jwt_decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=["HS256"]
                )
                user_id = decoded_data.get('user_id')
                
                scope['user'] = await get_user(user_id)
                print(f"✅ WebSocket Auth Başarılı: {scope['user'].username} (ID: {scope['user'].id})")
                
            except (InvalidToken, TokenError, KeyError) as e:
                print(f"❌ WebSocket Auth Hatası: {str(e)}")
                scope['user'] = AnonymousUser()
        else:
            print("⚠️ WebSocket Token bulunamadı!")
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)

