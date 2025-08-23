from django.urls import path
from accounts.views import SignInView, SignUpView, UserView

urlpatterns = [
    path('signin', SignInView.as_view(), name='signin'),
    path('signup', SignUpView.as_view(), name='signup'),
    path('me', UserView.as_view(), name='me'),
]
