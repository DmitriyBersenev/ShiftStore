from django.urls import path
from . import views

app_name = 'schedule_interface'
urlpatterns = [
    path('', views.index, name='index'),
    path('create_template/', views.create_templates, name='create_template'),
    path('create_template/get_form/', views.get_form_create_template, name='get_form_create_template'),
]
