

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from chat_app.tests import ChatMessageSocket, CallerWS1, CallerWS2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('api.urls')),
    path('chats/', include('chat_app.urls')),



    path('chat_test/', ChatMessageSocket.as_view()),
    path('caller1/', CallerWS1.as_view()),
    path('caller2/', CallerWS2.as_view())
]


if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)