import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if "apikey" in kwargs:
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:        
        # Get the row list in JSON as dealers
        dealers = json_result["Dealerships"]["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"],
                                   city=dealer_doc["city"],
                                   state=dealer_doc["state"],
                                   id=dealer_doc["id"],
                                   lat=dealer_doc["lat"],
                                   long=dealer_doc["long"],
                                   st=dealer_doc["st"],
                                   zip=dealer_doc["zip"],
                                   short_name=dealer_doc["short_name"],
                                   full_name=dealer_doc["full_name"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:        
        # Get the row list in JSON as dealers
        dealer = json_result["Dealerships"]
        # For each dealer object
        # for dealer in dealers:
        # Get its content in `doc` object
        dealer_doc = dealer["docs"][0]
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer_doc["address"],
                               city=dealer_doc["city"],
                               state=dealer_doc["state"],
                               id=dealer_doc["id"],
                               lat=dealer_doc["lat"],
                               long=dealer_doc["long"],
                               st=dealer_doc["st"],
                               zip=dealer_doc["zip"],
                               short_name=dealer_doc["short_name"],
                               full_name=dealer_doc["full_name"])
        #results.append(dealer_obj)

    return dealer_obj

def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        reviews = json_result["review"]
        for review in reviews:
            review_doc = reviews["docs"][0]
            review_obj = DealerReview(dealership=review_doc["dealership"],
                                      name=review_doc["name"],
                                      purchase=review_doc["purchase"],
                                      review=review_doc["review"],
                                      #purchase_date=review_doc["purchase_date"],
                                      purchase_date='',
                                      #car_make=review_doc["car_make"],
                                      car_make='',
                                      #car_model=review_doc["car_model"],
                                      car_model='',
                                      #car_year=review_doc["car_year"],
                                      car_year='',
                                      sentiment=analyze_review_sentiments(review_doc["review"]),                                      
                                      id=review_doc["id"])
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    API_KEY = 
    NLU_URL = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/6aa36569-933f-46ad-abc2-86e22ad3c795"
    authenticator = IAMAuthenticator(API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01', authenticator=authenticator)
    natural_language_understanding.set_service_url(NLU_URL)
    response = natural_language_understanding.analyze(text=text, features=Features(
        sentiment=SentimentOptions(targets=[text]))).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return(label)



