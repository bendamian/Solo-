from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Or 'home' if that's your homepage
            return redirect('solo_book_list')
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(
            self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')
