"""
URL configuration for Ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .import views  # Import views if necessary
from django.conf.urls import handler404
from django.contrib.auth import views as auth_views

# Custom 404 error handler
handler404 = 'Ecommerce.views.Erro404'

urlpatterns = [
    
    # Error page
    path("404", views.Erro404, name="404"),

    path("admin/", admin.site.urls),
    path("base/", views.BASE, name="base"),
    path("", views.HOME, name="home"),
    path("admin-home", views.ADMIN_HOME, name="admin_home"),
    path("about", views.ABOUT, name="about"),
    path("contact", views.CONTACT, name="contact"),
    path("product", views.PRODUCT, name="product"),
    path("search/", views.search_view, name="search"),
    
    path("product/<slug:slug>", views.PRODUCT_DETAILS, name="product_detail"),
    # account urls
    path("account/my_account", views.MY_ACCOUNT, name="my_account"),
    path("account/register", views.REGISTER, name="handleregister"),
    path("account/login", views.LOGIN, name="handlelogin"),
    path("account/profile", views.PROFILE, name="profile"),
    path("account/profile/update", views.PROFILE_UPDATE, name="profile_update"),
    path("accounts/logout/", views.LOGOUT, name="logout"),
     path('logout_confirmation/', views.logout_confirmation, name='logout_confirmation'),

    path("notification", views.Notifications, name="notification"),
    path("admin-notification", views.admin_notification, name="admin_notification"),
    path("delivery-notification", views.Delivery_notification, name="delivery_notification"),
    path("sales-notification", views.Sales_notification, name="sales_notification"),

    path("checkout", views.Checkout, name="checkout"),
    path('order-success/', views.order_success, name='order_success'),
    path("payment", views.Payment, name="payment"),
    path("order", views.Your_Order, name="order"),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    #Password reset: 
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # cart urls
    
    path("cart/add/<int:id>/", views.cart_add, name="cart_add"),
    path("cart/item_clear/<int:id>/", views.item_clear, name="item_clear"),
    path("cart/item_increment/<int:id>/", views.item_increment, name="item_increment"),
    path("cart/item_decrement/<int:id>/", views.item_decrement, name="item_decrement"),
    path("cart/cart_clear/", views.cart_clear, name="cart_clear"),
    path("cart/cart-detail/", views.cart_detail, name="cart_detail"),

    #Admin
    path('add_slider/', views.add_slider, name='add_slider'),
    path('edit_slider/<int:id>/', views.edit_slider, name='edit_slider'),
    path('delete_slider/<int:id>/', views.delete_slider, name='delete_slider'),
    #banners
    path('manage_banners/', views.manage_banners, name='manage_banners'),
    path('add_banner/', views.add_banner, name='add_banner'),
    path('edit_banner/<int:pk>/', views.edit_banner, name='edit_banner'),
    path('delete_banner/<int:pk>/', views.delete_banner, name='delete_banner'),
    #Main_category
    path('add_main_category/',views.add_main_category, name='add_main_category'),
    path('edit_main_category/<int:pk>/', views.edit_main_category, name='edit_main_category'),
    path('delete_main_category/<int:pk>/', views.delete_main_category, name='delete_main_category'),
    #category
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:pk>/', views.delete_category, name='delete_category'),
    #sub_category
    path('add_sub_category/', views.add_sub_category, name='add_sub_category'),
    path('edit_sub_category/<int:pk>/', views.edit_sub_category, name='edit_sub_category'),
    path('delete_sub_category/<int:pk>/', views.delete_sub_category, name='delete_sub_category'),


    #Products
    path('manage_products/', views.manage_products, name='manage_products'),
    #Section
    path('add-section/', views.add_section, name='add_section'),
    path('edit-section/<int:id>/', views.edit_section, name='edit_section'),
    path('delete-section/<int:id>/', views.delete_section, name='delete_section'),
    #Colour
    path('add-colour/', views.add_colour, name='add_colour'),
    path('edit-colour/<int:id>/', views.edit_colour, name='edit_colour'),
    path('delete-colour/<int:id>/', views.delete_colour, name='delete_colour'),
    #Brand
    path('add-brand/', views.add_brand, name='add_brand'),
    path('edit-brand/<int:id>/', views.edit_brand, name='edit_brand'),
    path('delete-brand/<int:id>/', views.delete_brand, name='delete_brand'),
    #Product
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    #Product_image
    path('product-images/', views.product_images, name='product_images'),
    path('add-product-image/', views.add_product_image, name='add_product_image'),
    path('product-autocomplete/', views.product_autocomplete, name='product_autocomplete'),
    path('edit-product-image/<int:image_id>/', views.edit_product_image, name='edit_product_image'),
    path('delete-product-image/<int:image_id>/', views.delete_product_image, name='delete_product_image'),
    #additional_information
    path('add-additional-information/', views.add_additional_information, name='add_additional_information'),
    path('delete-additional-information/<int:id>/', views.delete_additional_information, name='delete_additional_information'),
    #Orders
    path('all_orders/', views.all_Orders, name='all_orders'),
    #Delivery
    path('delivery_orders/', views.Delivery_orders, name='delivery_orders'),
    path('order/deliver/<int:order_id>/', views.deliver_order, name='deliver_order'),
    #Sales
    path('sales_orders/', views.sales_orders, name='sales_orders'),
    path('order/dispatch/<int:order_id>/', views.dispatch_order, name='dispatch_order'),
    path('order/out_for_delivery/<int:order_id>/', views.out_for_delivery_order, name='out_for_delivery_order'),
    path('notifications/mark_as_read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    #Apply job
    path('apply-for-job/', views.Apply_job, name='apply_job'),
     path('job_application/<int:application_id>/', views.job_application_detail, name='job_application_detail'),
    path('job_application/<int:application_id>/accept/', views.accept_job_application, name='accept_job_application'),
    path('job_application/<int:application_id>/reject/', views.reject_job_application, name='reject_job_application'),
    path('success/', views.success_page, name='success_page'),


    path("accounts/", include("django.contrib.auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

