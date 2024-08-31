from django.urls import path
from . import views
app_name = "accounts"

urlpatterns = [
     path('ajax/load-cities/', views.load_cities, name='load_cities'),  

    path("login/",views.LoginView.as_view(),name='login'),
    path("logout/",views.LogoutView.as_view(),name='logout'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'), 
    
    path('registration/step-1/', views.RegistrationStepOneView.as_view(), name='registration_step_one'),
    path('registration/step-2/', views.RegistrationStepTwoView.as_view(), name='registration_step_two'),
    path('registration/step-3/', views.RegistrationStepThreeView.as_view(), name='registration_step_three'),

    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),

    ]