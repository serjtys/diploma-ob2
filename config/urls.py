from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# Swagger imports
from rest_framework import permissions

# Swagger configuration
schema_view = get_schema_view(
    openapi.Info(
        title="ContentPlatform API",
        default_version="v1",
        description="API documentation for Paid Content Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@contentplatform.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Админка Django
    path("admin/", admin.site.urls),
    # Приложение core - главная страница и подписка
    path("", include("core.urls")),
    # Приложение users - регистрация и вход
    path("users/", include("users.urls")),
    # Swagger URLs
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# Для статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
