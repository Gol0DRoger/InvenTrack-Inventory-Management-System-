from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name="home"),
    path('login/', auth_views.LoginView.as_view(template_name='invapp/login.html'), name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('create/', views.product_create_view, name="product_create"),
    path('list/', views.product_list_view, name="product_list"),
    path('history/', views.audit_history_view, name="audit_history"),
    path('update/<int:product_id>/', views.product_update_view, name="product_update"),
    path('delete/<int:product_id>/', views.product_delete_view, name="product_delete"),
]