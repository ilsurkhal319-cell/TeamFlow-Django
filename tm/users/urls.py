from django.urls import path
from django.contrib.auth.views import LogoutView
from users.views import login, register

app_name = 'users'

urlpatterns = [
    path('login/',  login, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
]