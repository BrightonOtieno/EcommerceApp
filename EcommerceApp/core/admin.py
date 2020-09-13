from django.contrib import admin
from .models import OrderItem,Order,Item,BillingAddress,Payment,Coupon
# Register your models here.
def make_request_accepted(modeladmin,request,queryset):
    queryset.update(refund_request=False,refund_granted=True)

make_request_accepted.short_description ='update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                'ordered',
                'being_delivered',
                'received',
                'refund_request',
                'refund_granted',
                'billing_address',
                'payment',
                'coupon'
                ]  
    list_filter = [
        'being_delivered',
        'received',
        'refund_request',
        'refund_granted'
    ]
    list_display_links= [
        'billing_address',
        'payment',
        'coupon',
        'user'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]  
    actions = [make_request_accepted]
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Item)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(Coupon)