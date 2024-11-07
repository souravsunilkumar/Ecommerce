from django.contrib import admin
from .models import *

class ProductImage(admin.TabularInline):
    model =Product_Image

class Additional_Informations(admin.TabularInline):
    model=Additional_information

class Product_Admin(admin.ModelAdmin):
    inlines=(ProductImage, Additional_Informations)
    list_display =('product_name','price','categories','brand','colour','section')
    list_editable =('categories','brand','colour','section')

# Register your models here.
admin.site.register(slider)
admin.site.register(banner_area) 
admin.site.register(course_banner) 
admin.site.register(Main_category)
admin.site.register(Category)
admin.site.register(Sub_category)
admin.site.register(Section)
admin.site.register(Product,Product_Admin)
admin.site.register(Product_Image)
admin.site.register(Additional_information)
admin.site.register(Colour)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(Job_application)
admin.site.register(Review)
