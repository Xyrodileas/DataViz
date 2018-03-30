
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('success', views.upload_success, name='upload_success'),
    path('upload_data', views.upload_data, name='upload'),
    path('json', views.json, name='json'),
    path('tree', views.tree, name='tree'),
]
