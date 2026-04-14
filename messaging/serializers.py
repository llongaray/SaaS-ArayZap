from rest_framework import serializers


class SendMessageSerializer(serializers.Serializer):
    integration_id = serializers.IntegerField()
    numero = serializers.CharField(help_text="E.164 sem + ou com +")
    mensagem = serializers.CharField()
