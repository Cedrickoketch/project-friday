import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.accounts.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY

TIER_PRICE_MAP = {
    "pro": settings.STRIPE_PRICE_ID_PRO,
    "premium": settings.STRIPE_PRICE_ID_PREMIUM,
}


class CreateCheckoutSessionView(APIView):
    def post(self, request):
        tier = request.data.get("tier")
        if tier not in TIER_PRICE_MAP:
            return Response({"error": "Invalid tier."}, status=400)

        price_id = TIER_PRICE_MAP[tier]
        user = request.user

        # Get or create Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email, name=user.get_full_name())
            user.stripe_customer_id = customer.id
            user.save(update_fields=["stripe_customer_id"])

        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/dashboard?upgrade=success",
            cancel_url=f"{settings.FRONTEND_URL}/pricing?upgrade=cancelled",
            metadata={"user_id": str(user.id), "tier": tier},
        )
        return Response({"checkout_url": session.url})


class CustomerPortalView(APIView):
    def post(self, request):
        user = request.user
        if not user.stripe_customer_id:
            return Response({"error": "No subscription found."}, status=400)
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/dashboard",
        )
        return Response({"portal_url": session.url})


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session["metadata"].get("user_id")
            tier = session["metadata"].get("tier")
            if user_id and tier:
                User.objects.filter(id=user_id).update(tier=tier)

        elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
            customer_id = event["data"]["object"]["customer"]
            User.objects.filter(stripe_customer_id=customer_id).update(tier=User.TIER_FREE)

        return Response({"status": "ok"})
