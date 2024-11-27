from django.shortcuts import render
from accounts.views import logout
# Create your views here.

def index(request):
  logout(request)
  return render(request, 'home/index.html')