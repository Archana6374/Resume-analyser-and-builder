from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from builder.views import landing, login_view, register_view, logout_view, dashboard, chat_bot

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('accounts/', include('allauth.urls')),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', dashboard, name='profile'),
    path('api/chat/', chat_bot, name='chatbot'),
    path('analyzer/', include('analyzer.urls')),
    path('builder/', include('builder.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    
