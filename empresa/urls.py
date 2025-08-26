from django.contrib import admin
from django.urls import path
from .views import (
    EmpresaAPIView, EmpresaRetrieveUpdateDestroyAPIView,
    AtividadeListCreateAPIView, AtividadeRetrieveUpdateDestroyAPIView,
    SocioListCreateAPIView, SocioRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('empresa/', EmpresaAPIView.as_view(), name='empresa-list-create'),
    path('empresa/<str:documento>/',
         EmpresaRetrieveUpdateDestroyAPIView.as_view(), name='empresa-update-delete'),

    path('empresa/<str:documento>/atividades/', AtividadeListCreateAPIView.as_view(),
         name='empresa-list-create'),
    path('empresa/<str:documento>/atividades/<int:pk>/',
         AtividadeRetrieveUpdateDestroyAPIView.as_view(),
         name='empresa-atividades-detail'),

    path('empresa/<str:documento>/socios/',
         SocioListCreateAPIView.as_view(), name='empresa-socios'),
    path('empresa/<str:documento>/socios/<int:pk>/',
         SocioRetrieveUpdateDestroyAPIView.as_view(), name='empresa-socio-detail')
]
