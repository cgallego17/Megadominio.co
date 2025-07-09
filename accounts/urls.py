from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('resend-2fa/', views.resend_2fa_code, name='resend_2fa'),
    
    # Password Reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('dashboard/', views.client_dashboard, name='dashboard'),  # Alias para client_dashboard
    
    # Dashboard de clientes
    path('services/', views.client_services, name='client_services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),

    path('notifications/', views.client_notifications, name='client_notifications'),
    path('profile/', views.client_profile, name='client_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-detail/<str:order_number>/', views.order_detail, name='order_detail'),
    path('retry-payment/<str:order_number>/', views.retry_payment, name='retry_payment'),
    
    # AJAX
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # URLs de Wompi
    path('wompi/webhook/', views.wompi_webhook, name='wompi_webhook'),
    path('wompi/return/', views.wompi_return, name='wompi_return'),
    path('wompi/payment-methods/', views.wompi_payment_methods, name='wompi_payment_methods'),
    path('wompi/transaction/<str:transaction_id>/status/', views.wompi_transaction_status, name='wompi_transaction_status'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    
    # Páginas legales
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('accept-terms/', views.accept_terms, name='accept_terms'),
    path('check-terms-acceptance/', views.check_terms_acceptance, name='check_terms_acceptance'),
] 