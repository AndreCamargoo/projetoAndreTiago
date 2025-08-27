from django.urls import path

from fornecedores.views import FornecedorListCreateAPIView, FornecedorRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('fornecedores/', FornecedorListCreateAPIView.as_view(),
         name='fornecedor-list-create'),
    path('fornecedores/<int:pk>/', FornecedorRetrieveUpdateDestroyAPIView.as_view(),
         name='fornecedor-detail')
]
