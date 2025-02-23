from django.urls import path
from .views import InitiatePayment, VerifyPayment

urlpatterns = [
    path('initiate-payment/', InitiatePayment.as_view(), name='initiate-payment'),
    path('verify-payment/', VerifyPayment.as_view(), name='verify-payment'),
]