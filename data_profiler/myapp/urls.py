from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('charts/', views.charts, name="charts"),
    path('tables/', views.tables, name="tables"),
    path('password/', views.password, name="password"),
    path('signup/', views.signup, name="signup"),
    path('signout/', views.signout, name="signout"),
    path('signin/', views.signin, name="signin"),
    path('delete/', views.delete, name="delete"),
    path('main/', views.main, name="main"),
    path('settings/', views.settings, name="settings"),
]