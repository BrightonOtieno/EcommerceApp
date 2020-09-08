from django.shortcuts import render
from .models import Order,OrderItem,Item

# Create your views here.
def item_list_view(request):
    context  = {
        'items':Item.objects.all()
    }
    return render (request,'core/home-page.html',context)