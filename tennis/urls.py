from django.urls import path
from .views import tennis_tournaments, tournament

app_name = 'tennis'

urlpatterns = [
    path('tennis-tournaments/', tennis_tournaments, name="tennis-tournaments"),
    path('tournament/<int:pk>', tournament, name='tournament')
    # path('feedback', feedback, name="feedback"),
    # path('profile/<str:username>/', profile, name="profile"),
    # path('profile/<str:username>/edit/', edit, name='edit'),
    # path('<str:username>/', user_page, name='user_page'),
    # path('accounts/registration/', registration, name='registration')
]
