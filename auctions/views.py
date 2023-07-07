from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment
from .forms import ListingForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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
        listings = Listing.objects.all()
    else:
        listings = Listing.objects.filter(category=[c[0] for c in Listing.category.field.choices][index])

    return render(request, "auctions/index.html", {
        "category": [c[1] for c in Listing.category.field.choices][index],
        "listings": listings
    })


def listing_view(request, listing_id):
    # tu si stao + test
    if request.method == "POST":
        if request.POST["w_list"]:
            listing = Listing.objects.get(pk=listing_id)
            if request.POST["w_list"] == "add":
                request.user.watchlist.add(listing)
            else:
                request.user.watchlist.remove(listing)
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
        
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))
    comments = Comment.objects.filter(listing=listing_id)
    if listing in request.user.watchlist.all():
        watchlist = True
    else:
        watchlist = False
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "watchlist": watchlist
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
        user = authenticate(request)
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
