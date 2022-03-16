from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import Login, Logout
from backtest.views import BackTestAPIView, ListBackTestAPIView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('usuario/', include('users.routers')),
    path('tickers/', include('ticker.routers')),
    path('backtest/', BackTestAPIView.as_view(), name='backtest'),
    path('list-backtest/', ListBackTestAPIView.as_view(), name='list_backtest'),
    path('backtests/', include('backtest.routers')),




]
