from django.forms import ModelForm
from django import forms

from .models import User, Listing, Bid, Comment


class ListingForm(ModelForm):
    start_bid = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)

    class Meta:
        model = Listing
        fields = ["title", "category", "description", "image", "start_bid"]
