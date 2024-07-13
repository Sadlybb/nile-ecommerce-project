from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout


from .models import User
from .forms import UserRegisterForm


def user_register_view(request):
    form = UserRegisterForm

    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            messages.success(
                request, f"Hey {username}, Your account successfuly created.")

            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            new_user = authenticate(request, email=email, password=password)
            login(request, new_user)
            return redirect('store:homepage')

    context = {
        'form': form,
    }

    return render(request, 'userauth/register.html', context=context)


def user_login_view(request):

    if request.user.is_authenticated:
        return redirect('store:homepage')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)
                messages.success(request, f"Successfully logged in.")
                return redirect('store:homepage')
            else:
                messages.warning(request, "Please check your inputs.")

        except ObjectDoesNotExist:
            messages.warning(request, f"This Email:{email}is not registered.")
            return redirect('userauth:register')

    return render(request, 'userauth/login.html')


def user_logout_view(request):
    logout(request)
    messages.success(request, "Logged Out.")
    return redirect('userauth:login')
