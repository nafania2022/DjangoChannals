from django.urls import path
from django.contrib.auth.views import LogoutView


from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("chat/<str:room_name>/", views.room, name="room"),
    path("register/", views.register, name="register"),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('addfriend/', views.add_friends, name='addfriend'),
]
