from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


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
    



class Order(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField( auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)



    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        
        return total



    def __str__(self):
        return self.user.username
    


    
