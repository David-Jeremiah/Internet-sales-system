from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('', views.dashboard, name='dashboard'),
    path('sales/', views.sales_dashboard, name='sales_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Sales
    path('sale/new/', views.create_sale, name='create_sale'),
    path('sales/list/', views.sale_list, name='sale_list'),

    # Visits
    path('visit/log/', views.log_visit, name='log_visit'),
    path('visits/', views.visit_list, name='visit_list'),

    # Prospects
    path('prospects/', views.prospect_list, name='prospect_list'),

    # Admin views
    path('team/performance/', views.team_performance, name='team_performance'),
    path('feedback/analysis/', views.feedback_analysis, name='feedback_analysis'),

    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]