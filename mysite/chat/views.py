from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.views.generic import ListView
from .forms import UserRegistrationForm, LoginUserForm, FriendForm
from .models import User


def index(request):

    return render(request, "chat/index.html", {"title": "Главная страница",})


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name, "title": f"Комната для общения {room_name}"})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, f'Your account has been created. You can log in now!')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    context = {'form': form, 'title': 'Регистрация'}
    return render(request, 'chat/register.html', context)

def add_friends(request):
    form = FriendForm
    return render(request, 'chat/addfriends.html', {'form': form, 'title': 'Добавить друга'})


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'chat/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context

def logout_user(request):
    logout(request)
    return redirect('login')