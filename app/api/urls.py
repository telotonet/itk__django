from django.urls import path

from .views import FileUploadView, HTMLTableView, RecordListView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('records/', RecordListView.as_view(), name='record-list'),
    path('html/', HTMLTableView.as_view(), name='html-table'),
]
