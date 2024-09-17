from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class IndexView(TemplateView):
    template_name="website/index.html"

class ConditionsView(TemplateView):
    template_name='website/conditions.html'