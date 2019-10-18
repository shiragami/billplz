# -*- coding: utf-8 -*-
# Authors: Rafiq Rahim, Syukran Hakim

from django.conf.urls import url
from django.urls import path
from django.http import HttpResponse
from billplz import Billplz

# Django config
DEBUG = True
SECRET_KEY = 'secret' # Django secret key
ROOT_URLCONF = __name__

# Billplz config
BILLPLZ_API_KEY = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
BILLPLZ_SIGNATURE_KEY = 'x-xxxxxxxxxxxxxxxxxxxxxx'

def index(request):

    # Create order
    bp = Billplz(BILLPLZ_API_KEY,BILLPLZ_SIGNATURE_KEY, sandbox=True)
    
    # Order details
    collection_id = 'xxxxxxxx' # Billplz collection ID
    
    name = "Mr Test"
    email = "test@test.com"
    price = 10000 # Price in cents
    description = "Item A x 10"

    redirect_url = "http://127.0.0.1:8000/check-payment/"
    webhook_url  = "http://127.0.0.1:8000/callback/" # This will not work

    billplz_id, billplz_url = bp.create_bill(collection_id, name, price,
                                             webhook_url, description, email=email,
                                             redirect_url=redirect_url,
                                             )

    html = f"<a href='{billplz_url}'>Pay using Billplz</a>"

    return HttpResponse(html)


# Redirect after billplz payment
def check_payment(request):
    bp = Billplz(BILLPLZ_API_KEY,BILLPLZ_SIGNATURE_KEY, sandbox=True)

    form_data = request.GET.dict()

    # Check signature
    match = bp.verify_x_signature(form_data, 'redirect')

    if match:
        # Payment success
        # Thank you page
        return HttpResponse('OK')
    else:
        # Signature mismatch
        # Display error
        return HttpResponse('KO')
    pass


# Webhook to confirm payment succeed
# Note: callback will not work on localhost
def callback(request):
    bp = Billplz(BILLPLZ_API_KEY,BILLPLZ_SIGNATURE_KEY, sandbox=True)

    form_data = request.POST.dict()

    match = db.verify_x_signature(form_data, 'callback')

    if match:
        # Payment success
        # .. Process order
        return HttpResponse('OK')
    else:
        # Signature mismatch
        # .. Do not process order
        return HttpResponse('KO')
    pass


# Define URLs
urlpatterns = [
     path('', index),
     path('check-payment/', check_payment),
     path('callback/', callback),
]

