from django.contrib.auth.models import AbstractUser
from django.db import models

from .categories import CATEGORY_CHOICES


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)


class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    start_bid = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default="All Categories"
    )
    image = models.URLField(blank=True)
    active_status = models.BooleanField(default=True)


class Bid(models.Model):
    id = models.BigAutoField(primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    highest_bid_status = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=500)

