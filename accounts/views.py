from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegisterationForm, VerifyCodeForm, UserLoginForm
from .models import OtpCode, User
from django.contrib import messages
from utils import send_otp_code
import random
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin


class UserRegisterView(View):
    form_class = UserRegisterationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            randome_code = random.randint(1000, 9999)
            send_otp_code(phone_number=form.cleaned_data['phone_number'], code=randome_code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=randome_code)
            request.session['user_registration_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'full_name': form.cleaned_data['full_name'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'we sent you a message!', 'success')
            return redirect('accounts:verify_code')
        return render(request, self.template_name, {'form': form})
    

class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                if not code_instance.is_expierd():
                    User.objects.create_user(user_session['phone_number'], user_session['email'],
                                            user_session['full_name'], user_session['password'])
                else:
                    messages.warning(request, 'code was expierd :(', 'warning')
                    code_instance.delete()
                    return redirect('accounts:user_register')

                code_instance.delete()
                messages.success(request, 'user registerd succefuly', 'success')
                return redirect('home:home')
            else:
                messages.error(request, 'this code is not valid.', 'danger')
                return redirect('accounts:verify_code')
        return redirect('home:home')
    

class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, phone_number=cd['phone_number'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'user loged in successfully', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.warning(request, 'phone or password is wrong', 'warning')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'user loged out successfully', 'success')
        return redirect('home:home')
    

