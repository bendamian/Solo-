from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . forms import LoginForm, SignupForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required


#    context = {}
#    return render(request, './registration/dashboard.html',context)


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('users_app:login')
    else:
        form = SignupForm()

    return render(request, 'users/register.html', {
        'form': form
    })







@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


# - Authenticate a user





def login_user(request):

    form = LoginForm()

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
                login(request, user)
                return redirect('solo_app:solo_book_list')
        else:
                messages.success(
                    request, ("There Was An Error Logging In, Try Again..."))
                return redirect('users_app:login')

    context = {'form': form}
    return render(request, 'users/login.html', context=context)


def logout_user(request):
    logout(request)
    # auth.logout(request)
    messages.success(request, ("You Were Logged Out!"))
    return redirect("/")
