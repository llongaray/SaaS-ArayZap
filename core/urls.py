from django.urls import path

from core.views import BootstrapTokenView, TokenListCreateView, TokenRevokeView

urlpatterns = [
    path("tokens/bootstrap/", BootstrapTokenView.as_view(), name="token-bootstrap"),
    path("tokens/", TokenListCreateView.as_view(), name="token-list-create"),
    path("tokens/<int:pk>/", TokenRevokeView.as_view(), name="token-revoke"),
]
