from django.urls import path

from messaging.views import SendMessageView

urlpatterns = [
    path("messages/send/", SendMessageView.as_view(), name="message-send"),
]
