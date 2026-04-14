from django.urls import path

from webhooks.views import CrmWebhookView, MetaWebhookView

urlpatterns = [
    path("webhooks/crm/", CrmWebhookView.as_view(), name="webhook-crm"),
    path("meta/webhook/", MetaWebhookView.as_view(), name="meta-webhook"),
]
