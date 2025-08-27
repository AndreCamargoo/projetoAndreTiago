from django.urls import path

from planoDeContas.views import PlanoDeContasAPIView, PlanoDeContasRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('plano-de-contas/', PlanoDeContasAPIView.as_view(),
         name='plano-de-contas-list-create'),
    path('plano-de-contas/<int:pk>/', PlanoDeContasRetrieveUpdateDestroyAPIView.as_view(),
         name='plano-de-contas-detail')
]
