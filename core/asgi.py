"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# 1. Environment değişkenini ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. Django'yu başlat (Modelleri ve ayarları yüklemek için kritik)
django.setup()

# 3. HTTP application'ı al
django_asgi_app = get_asgi_application()

# 4. Channels bileşenlerini Django yüklendikten SONRA import et
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import game.routing 

# 5. JWT Middleware'i import et
from game.middleware import JWTAuthMiddleware

# 6. Application tanımını yap
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    ),
})