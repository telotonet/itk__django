from django.urls import path
from .views import FileUploadView, RecordListView, HTMLTableView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('records/', RecordListView.as_view(), name='record-list'),
    path('html-table/', HTMLTableView.as_view(), name='html-table'),
]
