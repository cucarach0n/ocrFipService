from apps.servicioOcr.api.views.ocr_views import FileOcrViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'uploadOCR',FileOcrViewSet, basename = 'uploadOCR-view')
urlpatterns = router.urls