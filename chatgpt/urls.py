
from django.urls import path
from .views import *

urlpatterns = [
    # path('', chat_page, name='chat_page'),
    path('chat/', chatbot_response, name='chat'),
    path('',home, name='home'),
     path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('history/', user_prompt_history, name='prompt_history'),
     path('logout/',logout_view, name='logout'),

]