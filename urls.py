
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('success', views.upload_success, name='upload_success'),
    path('upload_data', views.upload_data, name='upload'),
    path('json', views.json, name='json'),
    path('tree', views.tree, name='tree'),
    path('force_layout_json', views.force_layout_json, name='force_layout_json'),
    path('force_layout', views.force_layout, name='force_layout'),
    path('treemap_json', views.treemap_json, name='treemap_json'),
    path('treemap', views.treemap, name='treemap'),
    path('concentric_json/<int:skip>/', views.concentric_json, name='concentric_json'),
    path('concentric/<int:skip>/', views.concentric, name='concentric'),
    path('concentric_json', views.concentric_json, name='concentric_json'),
    path('concentric', views.concentric, name='concentric'),
]
