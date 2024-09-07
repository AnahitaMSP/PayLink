from django.urls import path
from .views import CreateVisitView ,VerifyPaymentView

app_name = 'visits'

urlpatterns = [
    path('create/', CreateVisitView.as_view(), name='create_visit'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='payment_verify'),

]
