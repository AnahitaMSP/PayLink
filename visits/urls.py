from django.urls import path
from .views import CreateVisitView, InvoiceDetailView, PaymentListView, CreatePaymentLinkView

app_name = 'visits'

urlpatterns = [
    path('create/', CreateVisitView.as_view(), name='create_visit'),
    path('invoices/<str:invoice_number>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<str:invoice_number>/create-payment-link/', CreatePaymentLinkView.as_view(), name='create_payment_link'),
    path('payments/<int:status>/', PaymentListView.as_view(), name='payment_list'),
]
