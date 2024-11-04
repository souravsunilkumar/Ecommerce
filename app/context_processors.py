from django.urls import reverse
from .models import Notification

def user_group_links(request):
    if request.user.is_authenticated:
        is_admin = request.user.groups.filter(id=1).exists()
        is_delivery = request.user.groups.filter(id=3).exists()
        is_sales = request.user.groups.filter(id=4).exists()

        home_url = reverse('admin_home') if is_admin else reverse('home')

        # Get notification counts
        delivery_notifications_count = Notification.objects.filter(
            user=request.user, is_read=False).count()

        admin_notifications_count = Notification.objects.filter(
            user=request.user, user__groups__id=1,  # Admin notifications
            is_read=False
        ).count()

        sales_notifications_count = Notification.objects.filter(
            user=request.user, user__groups__id=4,  # Sales notifications
            is_read=False
        ).count()

        return {
            'home_url': home_url,
            'is_admin': is_admin,
            'is_delivery': is_delivery,
            'is_sales': is_sales,
            'delivery_notifications_count': delivery_notifications_count,
            'admin_notifications_count': admin_notifications_count,
            'sales_notifications_count': sales_notifications_count,
        }
    else:
        return {
            'home_url': reverse('home'),
            'is_admin': False,
            'is_delivery': False,
            'is_sales': False,
            'delivery_notifications_count': 0,
            'admin_notifications_count': 0,
            'sales_notifications_count': 0,
        }
