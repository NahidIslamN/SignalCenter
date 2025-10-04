# asgi.py in project folder
"""
ASGI config for JVaitaks project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chat_app.routing import websocket_urlpatterns
from .custom_auth import CustomAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YourProjectName.settings')

# application = get_asgi_application()

# ASGI_APPLICATION = 'YourProjectName.asgi.application'



application = ProtocolTypeRouter(
    {
        'http':get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            CustomAuthMiddleware(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        )
    }
)



