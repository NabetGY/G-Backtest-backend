from rest_framework.routers import DefaultRouter
from ticker.views import TickerViewSet, TimeSeriesViewSet

router = DefaultRouter()

router.register( r'ticker', TickerViewSet)
router.register( r'time-series', TimeSeriesViewSet)

urlpatterns = router.urls