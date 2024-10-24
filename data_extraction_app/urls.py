from django.urls import path # type: ignore
from .views import FileUploadView
from .views import get_csrf_token

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('csrf-token/', get_csrf_token, name='csrf-token'),
]
