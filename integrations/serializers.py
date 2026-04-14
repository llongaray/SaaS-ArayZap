from rest_framework import serializers

from integrations.models import Integration


class IntegrationCreateSerializer(serializers.ModelSerializer):
    """Cria integração; credenciais em JSON conforme o tipo."""

    credentials = serializers.JSONField(write_only=True)

    class Meta:
        model = Integration
        fields = ("id", "name", "type", "session_name", "credentials")
        read_only_fields = ("id",)

    def validate(self, attrs):
        creds = attrs.get("credentials") or {}
        if attrs["type"] == Integration.TYPE_OFFICIAL:
            token = creds.get("access_token") or creds.get("permanent_token")
            if not creds.get("phone_number_id") or not token:
                raise serializers.ValidationError(
                    {
                        "credentials": "Para tipo official informe phone_number_id e access_token (ou permanent_token)."
                    }
                )
        elif attrs["type"] == Integration.TYPE_UNOFFICIAL:
            if not (creds.get("api_key") or creds.get("pywabot_api_key")):
                raise serializers.ValidationError(
                    {"credentials": "Para tipo unofficial informe api_key (ou pywabot_api_key)."}
                )
        return attrs

    def create(self, validated_data):
        creds = validated_data.pop("credentials")
        org = self.context["request"].user.organization
        inst = Integration(organization=org, **validated_data)
        inst.set_credentials(creds)
        if inst.type == Integration.TYPE_UNOFFICIAL and not inst.session_name:
            raise serializers.ValidationError(
                {"session_name": "Obrigatório para integrações não oficiais."}
            )
        inst.save()
        return inst


class IntegrationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = (
            "id",
            "name",
            "type",
            "status",
            "session_name",
            "last_error",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PairingRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        help_text="Número com DDI, só dígitos (ex.: 5511999999999).",
        max_length=20,
    )
