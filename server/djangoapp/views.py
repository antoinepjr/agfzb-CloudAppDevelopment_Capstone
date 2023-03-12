from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf,get_dealer_by_id_from_cf,get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        # pull from dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # check auth
        user = authenticate(username=username, password=password) 
        if user is not None:
            # login if valid
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    # get user from session id
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    # redirect back to the index.html
    return render(request, 'djangoapp/index.html', context)

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # Render page if GET request is called
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Get information about user from form
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            # Create new user
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/b08b2532-fe14-4f3d-9594-cdff4bd82bed/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context["dealership_list"] = dealerships
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/b08b2532-fe14-4f3d-9594-cdff4bd82bed/dealership-package/get-dealership.json"
        dealership = get_dealer_by_id_from_cf(url, dealer_id)
        context["dealer"] = dealership
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/b08b2532-fe14-4f3d-9594-cdff4bd82bed/dealership-package/get-review.json"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context["reviews"] = reviews

        #dealer_name = dealership.short_name
        #review_desc = ' '.join([review.review for review in reviews] + [review.sentiment for review in reviews])
        #return HttpResponse(dealer_name)
        #return HttpResponse(review_desc)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):    
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/b08b2532-fe14-4f3d-9594-cdff4bd82bed/dealership-package/get-dealership.json"
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars
        context["dealer"] = dealer
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/b08b2532-fe14-4f3d-9594-cdff4bd82bed/dealership-package/post-review"
        if (request.user.is_authenticated):
            review = {}
            review["id"] = 0
            review["dealership"] = dealer_id 
            review["name"] = request.POST["name"]
            review["review"] = request.POST["content"]
            if ("purchasecheck" in request.POST):
                review["purchase"] = True
            else:
                review["purchase"] = False
            if review["purchase"] == True:
                cars = CarModel.objects.filter(dealer_id=dealer_id)
                for car in cars:
                    if car.id == int(request.POST['car']):
                        review_car = car
                review["purchase_date"] = request.POST["purchase_date"]
                review["car_make"] = review_car.make.name
                review["car_model"] = review_car.name
                review["car_year"] = review_car.year.strftime("%Y")
            else:
                review["purchasedate"] = ""
                review["car_make"] = ""
                review["car_model"] = ""
                review["car_year"] = ""
        json_payload = {}
        json_payload["review"] = review
        response = post_request(url, json_payload, dealer_id=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
                


