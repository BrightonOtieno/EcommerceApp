from django.urls import path
from .views import Item_list_view,Item_detail_view,checkout_view,add_to_cart,remove_from_cart,OrderSummaryView,remove_single_item_from_cart,PaymentView,AddCouponView,RequestRefundView
urlpatterns = [
    path('',Item_list_view.as_view(),name='home-page'),
    path('product/<int:pk>/detail',Item_detail_view.as_view(),name='product-detail'),
    path('product/<int:pk>/add-to-cart',add_to_cart,name='add-to-cart'),
    path('product/<int:pk>/remove-from-cart',remove_from_cart,name='remove-from-cart'),
    path('product/<int:pk>/remove-single-item-from-cart',remove_single_item_from_cart,name='remove-single-item'),
    path('checkout/',checkout_view.as_view(),name='checkout-page'),
    path('payment/<payment_option>/',PaymentView.as_view(),name='payment'),
    path('order-summary/',OrderSummaryView.as_view(),name='order-summary'),
    path('add-coupon/',AddCouponView.as_view(),name='add-coupon'),
    path('request-refund/',RequestRefundView.as_view(),name='request-refund'),
]
