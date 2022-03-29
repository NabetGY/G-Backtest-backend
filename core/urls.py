from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="G-BACKTEST API",
      default_version='v1.0',
      description="Documentacion publica de G-BACKTEST",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="yoan.lopez@utp.edu.co"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


from users.views import Login, Logout, Register, UserUpdateAPIView, UserDeleteAPIView
from backtest.views import BackTestAPIView, ListBackTestAPIView

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', Register.as_view(), name='register'),
    path('update/', UserUpdateAPIView.as_view(), name='update-user'),
    path('delete/', UserDeleteAPIView.as_view(), name='delete-user'),
    path('usuario/', include('users.routers')),
    path('tickers/', include('ticker.routers')),
    path('backtest/', BackTestAPIView.as_view(), name='backtest'),
    path('list-backtest/', ListBackTestAPIView.as_view(), name='list_backtest'),
    path('backtests/', include('backtest.routers')),




]
