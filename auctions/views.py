from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal, InvalidOperation

from .models import User, Listing, Bid, Comment
from .forms import ListingForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active_status=True)
    })


def categories(request):
    ctgr = request.GET.get("c", None)  
    try:
        index = list(map(str.lower, [c[1].lower() for c in Listing.category.field.choices])).index(ctgr.lower())
    except ValueError:
        return HttpResponseRedirect(reverse("categories"))
    except AttributeError:
        return render(request, "auctions/categories.html", {
            "categories": [c[1] for c in Listing.category.field.choices]
        })

    if index == 0:
        listings = Listing.objects.filter(active_status=True)
    else:
        listings = Listing.objects.filter(category=[c[0] for c in Listing.category.field.choices][index], active_status=True)

    return render(request, "auctions/index.html", {
        "category": [c[1] for c in Listing.category.field.choices][index],
        "listings": listings
    })


def listing_view(request, listing_id):
    # tu si stao
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        if request.POST.get("w_list"):
            if request.POST.get("w_list") == "add":
                request.user.watchlist.add(listing)
            elif request.POST.get("w_list") == "remove":
                request.user.watchlist.remove(listing)
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
        if request.POST.get("cmnt"):
            new_comment = Comment(commenter=request.user, listing=listing, text=request.POST.get("cmnt"))
            new_comment.save()
        if request.POST.get("bd"):
            try:
                amount = Decimal(request.POST.get("bd"))
            except InvalidOperation:
                messages.error(request, "Invalid bid.")
            else:
                try:
                    current_bid = listing.bids.get(highest_bid=True)
                    price = current_bid.amount
                except Bid.DoesNotExist:
                    current_bid = None
                    price = listing.start_price
                if current_bid:
                    if amount > price:
                        current_bid.highest_bid = False
                        current_bid.save()
                        new_bid = Bid(buyer=request.user, listing=listing, amount=amount)
                        new_bid.save()
                    else:
                        messages.error(request, "Your bid must be greater than the previous bid.")
                else:
                    if amount >= price:
                        new_bid = Bid(buyer=request.user, listing=listing, amount=amount)
                        new_bid.save()
                    else:
                        messages.error(request, "Your bid must be at least as large as the starting price.")
        if request.POST.get("close"):
            if request.user == listing.seller:
                listing.active_status = False
                try:
                    listing.buyer = listing.bids.get(highest_bid=True).buyer
                except Bid.DoesNotExist:
                    pass
                listing.save()

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))
   
    comments = Comment.objects.filter(listing=listing_id)

    try:
        if listing in request.user.watchlist.all():
            watchlist = True
        else:
            watchlist = False
    except AttributeError:
        watchlist = None

    try:
        bid = listing.bids.get(highest_bid=True)
    except Bid.DoesNotExist:
        bid = None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "watchlist": watchlist,
        "bid": bid,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.seller = request.user
            new_listing.save()
            form.save_m2m()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def watchlist(request):
    return render(request, "auctions/index.html", {
        "category": "Watchlist",
        "listings": request.user.watchlist.all()
    })
