from .models import Listing


class AuctionsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.watchlist_count = len(request.user.watchlist.all())
        except AttributeError:
            pass
        else:
            request.my_listings_count = len(Listing.objects.filter(seller=request.user))
            request.bought_items_count = len(Listing.objects.filter(buyer=request.user))
        response = self.get_response(request)
        return response
