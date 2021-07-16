from django.urls import path
from . import views

app_name = 'structure'
urlpatterns = [
    path('', views.index, name='index'),
    path('create_person/', views.create_person, name='create_person'),
    path('remove_person/', views.remove_person, name='remove_person'),
    path('fire_person/', views.fire_person, name='fire_person'),
    path('transfer_person/', views.transfer_person, name='transfer_person'),
]
