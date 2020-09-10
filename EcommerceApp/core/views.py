from django.shortcuts import render,redirect,get_object_or_404,redirect
from .models import Order,OrderItem,Item
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
class Item_list_view(ListView):
    template_name = 'core/home-page.html'
    context_object_name = 'items'
    model  = Item
# Item Detail View
class Item_detail_view(DetailView):
    template_name = 'core/product.html'
    context_object_name = 'item'
    model  = Item
class OrderSummaryView(LoginRequiredMixin,View):

    def get(self,*args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            context ={
                'order':order
            }
            return render (self.request,'core/order_summary.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request,"you do not have an active order ")
            return redirect('/')
        



def checkout_view(request):
    return render(request,'core/checkout-page.html')

@login_required
def add_to_cart(request,pk):
    # get the product(item) passed in from the url with its pk
    item = get_object_or_404(Item,pk=pk)
    # adding/creating an order item for the product
    order_item, created = OrderItem.objects.get_or_create(item=item,ordered=False,user=request.user)
    # get incomplete order of the user( filter Order by User and ordered=False meaning hasnt been bought already)
    
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    # order_qs is a query_set an (ARRAY/LIST) get the first value
    # Cheking if the incomplete order exists  and get the first one
    if order_qs:
        order = order_qs[0]
        # check if that order_item exist in the order
        # if it exists update its quantity by 1
        if order.items.filter(item__pk = item.pk).exists():
            order_item.quantity +=1
            order_item.save()
            messages.success(request,'Item quantity was updated ')
            return redirect('order-summary')
        # if order item is not in the order add it

        else:
            order.items.add(order_item)
            messages.success(request,'Item was added to your cart ')
    # if the order does not exist
    # create a new order
    # and add that order item to it
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user,order_date=order_date)
        order.items.add(order_item)
        messages.success(request,'Item was added to your cart ')
    # redirect the user back to that products url
    return redirect('product-detail',pk=pk)


@login_required
def remove_from_cart(request,pk):
    item = get_object_or_404(Item,pk=pk)

    order_qs = Order.objects.filter(user=request.user,ordered=False)

    if order_qs:
        order = order_qs[0]
        # check if item exists in the Order  
        if order.items.filter(item__pk = item.pk).exists():
            # get that  orderItem with that passed item(product)
            order_item = OrderItem.objects.filter(item=item,
            ordered=False,
            user=request.user
            )[0]

            order.items.remove(order_item)
        
            messages.info(request,'Item was removed from  your cart ')
            # if order item is not in the order send a message
            return redirect('order-summary')
        else:
            return redirect('product-detail',pk=pk)
            messages.info(request,'Item  Does not exist in   your cart please add it ')
    # if the order does not exist send message

    else:
        messages.info(request,"You don't have an active order")
        return redirect('product-detail',pk=pk)
    
    return redirect('product-detail',pk=pk)

@login_required
def remove_single_item_from_cart(request,pk):
    item = get_object_or_404(Item,pk=pk)

    order_qs = Order.objects.filter(user=request.user,ordered=False)

    if order_qs:
        order = order_qs[0]
        # check if item exists in the Order  
        if order.items.filter(item__pk = item.pk).exists():
            # get that  orderItem with that passed item(product)
            order_item = OrderItem.objects.filter(item=item,
            ordered=False,
            user=request.user
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

        
            messages.info(request,'Item quantity was updated successfully')
            return redirect('order-summary')
            # if order item is not in the order send a message
        else:
            messages.info(request,'Item  Does not exist in   your cart please add it ')
            return redirect('product-detail',pk=pk)
            
    # if the order does not exist send message

    else:
        messages.info(request,"You don't have an active order")
        return redirect('product-detail',pk=pk)
    
    return redirect('product-detail',pk=pk)

