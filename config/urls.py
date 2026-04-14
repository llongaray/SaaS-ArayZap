"""URLs raiz — apenas API REST e schema OpenAPI."""
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

urlpatterns = [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path("api/", include("core.urls")),
    path("api/", include("integrations.urls")),
    path("api/", include("messaging.urls")),
    path("api/", include("webhooks.urls")),
]
