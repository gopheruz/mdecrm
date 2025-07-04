from django.urls import path

from user_app.views import *

urlpatterns = [
    path('login/', login_view, name='login_url'),
    path('logout/', logout_view, name='logout_url'),
    path('authenticate/logging/user/', authenticate_user_view, name='authenticate_user_url'),
]
