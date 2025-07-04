from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate



from user_app.forms import LoginForm


def login_view(request):
    form = LoginForm()

    context = {
        'form': form,
        'title': 'Вход'
    }

    return render(request, 'user_app/login.html', context)

def authenticate_user_view(request):
    form = LoginForm(data=request.POST)

    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, "Вы вошли в аккаунт оператора !")
            return redirect('index_url')
        else:
            messages.error(request, "Логин или пароль не правильный !")
            return redirect('login_url')
    else:
        messages.error(request, "Логин или пароль не правильный !")
        return redirect('login_url')

def logout_view(request):
    logout(request)
    messages.warning(request, "Вы вышли с аккаунта !")
    return redirect('index_url')