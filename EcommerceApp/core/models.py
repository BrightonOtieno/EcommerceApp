from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField

# Create your models here.
CATEGORY_CHOICES = (
    ('S','Shirt'),
    ('SW','Sports Wear'),
    ('OW','Outwear')
)
LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)
SALE_STATE_CHOICES = (
    ('N','New'),
    ('BS','BestSeller'),
    ('B','Best')
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    label = models.CharField(choices=LABEL_CHOICES, max_length=1,default="P")
    category= models.CharField(choices=CATEGORY_CHOICES, max_length=2,default="S")
    state= models.CharField(choices=SALE_STATE_CHOICES, max_length=2,default="N")
    discount_price = models.FloatField(blank=True,null=True)
    description = models.TextField()
    image = models.ImageField(upload_to = 'product_images')

    # Absolute url for product/item detail
    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk": self.id})

    # Absolute url for adding product / item to the Cart
    def get_add_item_to_cart(self):
        return reverse("add-to-cart", kwargs={"pk": self.id})


    def get_remove_item_from_cart(self):
        return reverse("remove-from-cart", kwargs={"pk": self.id})
    

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    user = models.ForeignKey(User,  on_delete=models.CASCADE,blank=True,null=True)

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_item_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return  self.get_total_item_price() - self.get_total_item_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_item_discount_price()
        return self.get_total_item_price()

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

class Coupon(models.Model):
    code =  models.CharField( max_length=20)
    amount  = models.FloatField()

    def __str__(self):
        return self.code

    

class Order(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ref_code = models.CharField( max_length=20)
    start_date = models.DateTimeField( auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,blank=True,null=True)
    payment = models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
    coupon =  models.ForeignKey('Coupon',on_delete=models.SET_NULL,blank=True,null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_request = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)


    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount

        print(total)

        return  total


    def __str__(self):
        return self.user.username
    

class BillingAddress(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    street_address = models.CharField( max_length=100)
    zip_code = models.CharField( max_length=100)
    country = CountryField(multiple=False)
    apartment_address = models.CharField( max_length=100)


    def  __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField( max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True,null=True)
    amount  = models.FloatField()
    timestamp = models.DateTimeField( auto_now_add=True)


    def __str__(self):
        return self.user.username
    
class Refund(models.Model):
    order  = models.ForeignKey('Order',  on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.pk}"