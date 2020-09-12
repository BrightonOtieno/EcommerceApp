from django.conf import settings
from django.shortcuts import render,redirect,get_object_or_404,redirect
from .models import Order,OrderItem,Item,BillingAddress,Payment,Coupon
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckOutForm,CouponForm
import stripe
stripe.api_key = settings.STRIPE_SECRETE_KEY



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
            messages.warning(self.request,"you do not have an active order ")
            return redirect('/')
        



class checkout_view(View):
    def get(self,*args, **kwargs):
        form = CheckOutForm()
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            context = {
            'form':form,
            'order':order,
            'CouponForm':CouponForm(),
            'DISPLAY_COUPON_FORM':True
            }
            return render(self.request,'core/checkout-page.html',context)

        
        except ObjectDoesNotExist:
            messages.warning(self.request,"you do not have an active order ")
            return redirect(self.request,'core/checkout-page.html')
        
    
    def post(self,*args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            #print(self.request.POST)
            if form.is_valid():
                print('For validated Successfully')
                print(self.request.POST)
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                zip_code = form.cleaned_data.get('zip_code')
                country= form.cleaned_data.get('country')
                # same_billing_address = form.cleaned_data.get('same_billing_address)
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    zip_code=zip_code,
                    country = country

                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: Check users payment option and redirect to that payment page
                if payment_option == 'S':
                    return redirect('payment',payment_option='Stripe')
                elif payment_option == 'P':
                    return redirect('payment',payment_option='Stripe')
                else:
                    messages.info(self.request,'Invalid payment options')
                    return redirect('checkout-page')
            else:
                messages.warning(self.request,'Checkout Failed')
                return redirect('checkout-page')
        except ObjectDoesNotExist:
            messages.warning(self.request,"you do not have an active order ")
            return redirect('/')

class PaymentView(View):
    def get(self,*args, **kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        if order.billing_address: # only if the BillingAddressForm was FILLED
            context= {
                'order':order,
                'DISPLAY_COUPON_FORM':False
            }
            return render(self.request,'core/payment.html',context)

        else:
            messages.info(self.request,'You havent filled the billing address form ')
            return redirect ('checkout-page')


    def post(self,*args, **kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
    # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            
            # PAYMENT INSTANCE

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

        
            # update each order_item as ordered(=>ordered=True)

            order_items = order.items.all()
            order_items.update(ordered=True)
            for order_item in order_items:
                order_item.save()

            # now set the ordered to True 
            order.ordered = True
            order.payment = payment
            order.save()



            messages.success(self.request,"Your order was successful")
            return redirect('/')

        
        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error.{}')
            messages.warning(self.request,f"{err.get('message')}")
            return redirect('/')
        
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.warning(self.request,"Rate Limit Error")
            return redirect('/')
    
        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request,"Invalid Parameters")
            return redirect('/')
        
        except stripe.error.AuthenticationError as e: 
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.info(self.request,"Not Authenticated")
            return redirect('/')
        
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            messages.warning(self.request,"Network Error")
            return redirect('/')
        
        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            messages.warning(self.request,"Something went wrong you were not charged .Please try again")
    
        except Exception as e:
        # Something else happened, completely unrelated to Stripe
            messages.warning(self.request,"Serious error it is we have been notified")
            return redirect('/')
    
    

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
            ####
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

            # TODO:when item is removed from cart set it quantity to (default = 1)
            order_item.quantity = 1
            order_item.save()

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


def get_coupon(request,code):
    # checks if coupon with that code exists
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request,'This Coupon Does not exist')
        return redirect ('checkout-page')

class AddCouponView(View):
    # adds the coupon to the order 
    def post(self,*args,**kwargs):
        form = CouponForm(request.POST or None)

        if form.is_valid():

            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user,ordered=False)
                order.coupon = get_coupon(self.request,code)
                order.save()
                messages.success(self.request,"Successfully added coupon")
                return redirect('checkout-page')
            except ObjectDoesNotExist:
                messages.warning(self.request,'You do not have an active order')
                return redirect ('checkout-page')
    # if request is a GET WE dont support that 



