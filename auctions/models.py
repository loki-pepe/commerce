from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

from .categories import CATEGORY_CHOICES


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchers")


class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name="listings")
    title = models.CharField(blank=False, null=False, max_length=64)
    description = models.CharField(max_length=500)
    start_price = models.DecimalField(blank=False, null=False, max_digits=12, decimal_places=2, validators=[MinValueValidator(limit_value=0)])
    # current_bid = models.OneToOneField("Bid", on_delete=models.PROTECT, null=True, related_name="_listing")
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default="All Categories"
    )
    image = models.URLField(blank=True, null=True)
    active_status = models.BooleanField(default=True)
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, default=None, null=True, blank=True, related_name="bought_listings")

    def __str__(self):
        return f"Listing: {self.title}({self.id}) by {self.seller}({self.seller.id})"


class Bid(models.Model):
    id = models.BigAutoField(primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    highest_bid = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Bid number {self.id} of ${self.amount} by {self.buyer}({self.buyer.id}) for ({self.listing})"


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(null=False, blank=False, max_length=500)

    def __str__(self):
        return f"Comment number {self.id} by {self.commenter}({self.commenter.id}) regarding {self.listing}:\n{self.text}"
