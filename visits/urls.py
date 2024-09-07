from django.urls import path
from .views import CreateVisitView , VisitSuccessView,VerifyPaymentView

app_name = 'visits'

urlpatterns = [
    path('create/', CreateVisitView.as_view(), name='create_visit'),
    path('success/', VisitSuccessView.as_view(), name='visit_success'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='payment_verify'),

]
