from django.urls import path
from .views import DatasetUploadView, DatasetListView, GlobalDatasetListView, DatasetRecordsView, DatasetStatsView, DatasetPDFView
from rest_framework.authtoken import views

urlpatterns = [
    path('upload/', DatasetUploadView.as_view(), name='dataset-upload'),
    path('datasets/', DatasetListView.as_view(), name='dataset-list'),
    path('global-datasets/', GlobalDatasetListView.as_view(), name='global-dataset-list'),
    path('datasets/<int:id>/data/', DatasetRecordsView.as_view(), name='dataset-records'),
    path('datasets/<int:id>/stats/', DatasetStatsView.as_view(), name='dataset-stats'),
    path('datasets/<int:id>/pdf/', DatasetPDFView.as_view(), name='dataset-pdf'),
    path('api-token-auth/', views.obtain_auth_token),
]
