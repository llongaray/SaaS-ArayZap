from rest_framework import serializers


class CrmWebhookSerializer(serializers.Serializer):
    url = serializers.URLField()
    secret = serializers.CharField(required=False, allow_blank=True, default="")
