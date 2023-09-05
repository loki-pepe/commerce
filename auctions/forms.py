from django.forms import ModelForm
from django import forms

from .models import User, Listing, Bid, Comment


class ListingForm(ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "64 characters max", "maxlength": "64"}
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "500 characters max", "maxlength": "500"}
        )
    )
    start_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        widget=forms.TextInput(attrs={"placeholder": "$"}),
    )
    image = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "URL (optional)"})
    )

    class Meta:
        model = Listing
        fields = ["title", "category", "description", "image", "start_price"]
