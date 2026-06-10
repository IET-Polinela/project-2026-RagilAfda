from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages

from .forms import RegisterForm


# REGISTER (CITIZEN)
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = False
            user.save()

            messages.success(request, "Registrasi berhasil! Silakan login 👤")
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'usermanagement_24782091/register.html', {'form': form})


# LOGIN
class CustomLoginView(LoginView):
    template_name = 'usermanagement_24782091/login.html'

    def get_success_url(self):
        return '/'   # atau 'report_list'
    
    def form_valid(self, form):
        messages.success(self.request, "Login berhasil.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Username atau password salah.")
        return super().form_invalid(form)

# LOGOUT
class CustomLogoutView(LogoutView):
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Logout berhasil.")
        return super().dispatch(request, *args, **kwargs)