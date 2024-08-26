from django.urls import path
from .views import CreateVisitView, VisitSuccessView, go_to_gateway_view, callback_gateway_view

app_name = 'visits'

urlpatterns = [
    path('create/', CreateVisitView.as_view(), name='create_visit'),
    path('gateway/<int:visit_id>/', go_to_gateway_view, name='go_to_gateway'),
    path('callback/', callback_gateway_view, name='callback_gateway'),
    path('success/', VisitSuccessView.as_view(), name='visit_success'),]