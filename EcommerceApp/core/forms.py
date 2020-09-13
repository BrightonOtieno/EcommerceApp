from django import forms
from django_countries.fields import CountryField 
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('P','Paypal')
)

class CheckOutForm(forms.Form):
    street_address = forms.CharField(required=True ,widget=forms.TextInput(
        attrs={
            'class':'form-control'
        }
    ))
    apartment_address= forms.CharField(required=False,widget=forms.TextInput(
        attrs={
            'class':'form-control my-2'
        }
    ))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(
            attrs= {
        'class':'custom-select d-block w-100'
            }
    )
    
        )
    zip_code = forms.CharField()
    same_billing_address = forms.BooleanField(required=False,widget=forms.CheckboxInput())
    save_info = forms.BooleanField(required=False,widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,
    choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(required=False,widget=forms.TextInput(
        attrs={
            'class': "form-control",
            'placeholder':"Promo code" ,
            'aria-label':"Recipient's username",
            'aria-describedby':"basic-addon2"
        }
    ))



class RefundForm(forms.Form):
    ref_code = forms.CharField(required=True,widget=forms.TextInput(
        attrs={
            'class': "form-control",
            'placeholder':"reference code" ,
            'aria-label':"Recipient's reference code",
        
        }
    ))

    message = forms.CharField(required=True,widget=forms.Textarea(
        attrs={
            'class':'form-control',
            'rows':4
        }
    )
       
    )
    email = forms.EmailField(required=True,widget=forms.TextInput(
        attrs = {
            'class':'form-control'
        }
    ))

