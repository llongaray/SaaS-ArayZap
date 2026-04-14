from django.urls import path

from integrations.views import (
    IntegrationDetailView,
    IntegrationListCreateView,
    IntegrationPairingView,
    IntegrationSessionDeleteView,
)

urlpatterns = [
    path("integrations/", IntegrationListCreateView.as_view(), name="integration-list"),
    path("integrations/<int:pk>/", IntegrationDetailView.as_view(), name="integration-detail"),
    path(
        "integrations/<int:pk>/pairing/",
        IntegrationPairingView.as_view(),
        name="integration-pairing",
    ),
    path(
        "integrations/<int:pk>/session/",
        IntegrationSessionDeleteView.as_view(),
        name="integration-session-delete",
    ),
]
