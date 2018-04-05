
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
    path('concentric_json', views.concentric_json, name='concentric_json'),
    path('concentric', views.concentric, name='concentric'),
    path('circular_tree_json', views.circular_tree_json, name='circular_tree_json'),
    path('circular_tree', views.circular_tree, name='circular_tree'),
    path('histogram_json', views.histogram_json, name='histogram_json'),
    path('histogram', views.histogram, name='histogram'),
]
