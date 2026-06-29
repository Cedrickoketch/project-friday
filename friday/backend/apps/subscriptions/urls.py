from django.urls import path
from .views import CreateCheckoutSessionView, CustomerPortalView, StripeWebhookView

urlpatterns = [
    path("checkout/", CreateCheckoutSessionView.as_view(), name="checkout"),
    path("portal/", CustomerPortalView.as_view(), name="portal"),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
