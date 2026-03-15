from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def contacts(request):
    return render(request, 'contacts/contacts.html')
