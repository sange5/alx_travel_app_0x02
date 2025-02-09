import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment

class InitiatePayment(APIView):
    def post(self, request):
        booking_reference = request.data.get('booking_reference')
        amount = request.data.get('amount')
        email = request.data.get('email')

        if not booking_reference or not amount or not email:
            return Response({"error": "Booking reference, amount, and email are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare Chapa API request
        url = "https://api.chapa.co/v1/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "tx_ref": booking_reference,
            "callback_url": "http://yourfrontend.com/payment-success",  
            "return_url": "http://yourbackend.com/api/payments/verify-payment/",  
        }

        #  request to Chapa API
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            transaction_id = data.get('data', {}).get('id')

            # Save payment details
            Payment.objects.create(
                booking_reference=booking_reference,
                amount=amount,
                transaction_id=transaction_id,
                payment_status="Pending"
            )

            return Response({"payment_url": data['data']['checkout_url']}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPayment(APIView):
    def post(self, request):
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response({"error": "Transaction ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch payment details from Chapa
        url = f"https://api.chapa.co/v1/transaction/verify/{transaction_id}"
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            payment_status = data.get('data', {}).get('status')

            # Update payment status in the database
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.payment_status = payment_status
            payment.save()

            return Response({"status": payment_status}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)