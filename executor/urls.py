from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('<uuid:model_id>', views.executor, name="executor")
]