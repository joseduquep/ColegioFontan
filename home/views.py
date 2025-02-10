from django.shortcuts import render
from accounts.views import logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
  logout(request)
  return render(request, 'home/index.html')

@login_required
def home(request):
   return render(request, 'home/home.html')

def handler404(request, exception):
    return render(request, '404.html', status=404)