from rest_framework import serializers

from core.models import ApiToken, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "created_at")
        read_only_fields = fields


class ApiTokenCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, default="")


class ApiTokenResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    prefix = serializers.CharField()
    name = serializers.CharField()
    token = serializers.CharField(help_text="Mostrado apenas na criação.")
    created_at = serializers.DateTimeField()


class BootstrapSerializer(serializers.Serializer):
    bootstrap_secret = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(max_length=255)
