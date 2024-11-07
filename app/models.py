from django.db import models as m
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


# Create your models here.


class slider(m.Model):
    DISCOUNT_DEAL = (
        ("HOT DEALS", "HOT DEALS"),
        ("New Arivals", "New Arivals"),
    )

    Image = m.ImageField(upload_to="media/slider_imgs")
    Discount_Deal = m.CharField(choices=DISCOUNT_DEAL, max_length=100)
    Sale = m.IntegerField()
    Brand_Name = m.CharField(max_length=200)
    Discount = m.IntegerField()
    Link = m.CharField(max_length=200)

    def __str__(self):
        return self.Brand_Name


class banner_area(m.Model):
    image = m.ImageField(upload_to="media/banner_img")
    Discount_Deal = m.CharField(max_length=100)
    Quotes = m.CharField(max_length=100)
    Discount = m.IntegerField(null=True, blank=True)
    Link = m.CharField(max_length=200,null=True, blank=True)

    def __str__(self):
        return self.Quotes

class course_banner(m.Model):
    image = m.ImageField(upload_to="media/course_banner_img")
    Course = m.CharField(max_length=100)
    Quotes = m.CharField(max_length=100)
    Link = m.CharField(max_length=200,null=True, blank=True)

    def __str__(self):
        return self.Course

class Main_category(m.Model):
    name = m.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(m.Model):
    main_category = m.ForeignKey(Main_category, on_delete=m.CASCADE)
    name = m.CharField(max_length=100)

    def __str__(self):
        return self.name + " -- " + self.main_category.name


class Sub_category(m.Model):
    category = m.ForeignKey(Category, on_delete=m.CASCADE)
    name = m.CharField(max_length=100)

    def __str__(self):
        return (
            self.category.main_category.name
            + "--"
            + self.category.name
            + "--"
            + self.name
        )


class Section(m.Model):
    name = m.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Colour(m.Model):
    code= m.CharField(max_length=100)

    def __str__(self):
        return self.code
    
class Brand(m.Model):
    name=m.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(m.Model):
    total_quantity = m.IntegerField()
    availability = m.IntegerField()
    featured_image = m.ImageField(upload_to='product_images/')
    product_name = m.CharField(max_length=100)
    brand = m.ForeignKey('Brand', on_delete=m.CASCADE, null=True)
    price = m.IntegerField()
    discount = m.IntegerField()
    tax = m.IntegerField(null=True)
    packing_cost = m.IntegerField(null=True)
    product_information = RichTextUploadingField(null=True)
    model_name = m.CharField(max_length=100,null=True, blank=True)
    categories = m.ForeignKey('Sub_category', on_delete=m.CASCADE)
    colour = m.ForeignKey('Colour', on_delete=m.CASCADE, null=True,blank=True)
    tags = m.CharField(max_length=100)
    description = RichTextUploadingField(null=True)
    section = m.ForeignKey('Section', on_delete=m.DO_NOTHING)
    slug = m.SlugField(default='', max_length=500, null=True, blank=True)
    average_rating = m.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    def __str__(self):
        return self.product_name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={'slug': self.slug})

    class Meta:
        db_table = "app_Product"


def create_slug(instance, new_slug=None):
    slug = slugify(instance.product_name)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Product)




class Product_Image(m.Model):
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    images = m.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.product_name}"


class Additional_information(m.Model):
    product = m.ForeignKey(Product, on_delete=m.CASCADE)
    specification = m.CharField(max_length=100)
    detail =m.CharField(max_length=100)


class Order(m.Model):
    product_image = m.URLField()
    product_name = m.CharField(max_length=255)
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    quantity = m.IntegerField()
    unit_price = m.DecimalField(max_digits=10, decimal_places=2)
    total_price = m.DecimalField(max_digits=10, decimal_places=2)
    first_name = m.CharField(max_length=100)
    last_name = m.CharField(max_length=100)
    email = m.EmailField()
    phone = m.CharField(max_length=15)
    address = m.TextField()
    city = m.CharField(max_length=100)
    state = m.CharField(max_length=100)
    country =m.CharField(max_length=100,null=True)
    postcode = m.CharField(max_length=10)
    payment_method = m.CharField(max_length=50)
    order_status =m.CharField(max_length=100,null=True)
    date_ordered = m.DateTimeField(auto_now_add=True)
    total_amount_paid = m.DecimalField(max_digits=10, decimal_places=2)
    payment_order_id = m.CharField(max_length=100, blank=True, null=True)
    payment_id=m.CharField(max_length=100, blank=True, null=True)
    payment_signature=m.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order by {self.user.username} for {self.product_name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)




    class Meta:
        db_table = "app_order"

class Job_application(m.Model):
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    first_name = m.CharField(max_length=30)
    last_name = m.CharField(max_length=30)
    date_of_birth = m.DateField()
    phone_number = m.CharField(max_length=15)
    address = m.TextField()
    educational_qualification = m.CharField(max_length=255)
    JOB_TYPE_CHOICES = [
        ('sales', 'Sales'),
        ('delivery', 'Delivery'),
    ]
    type_of_job = m.CharField(max_length=10, choices=JOB_TYPE_CHOICES)
    applied_at = m.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type_of_job}"

class Notification(m.Model):
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    job_application = m.ForeignKey(Job_application, on_delete=m.CASCADE, null=True, blank=True)
    message = m.TextField()
    is_read = m.BooleanField(default=False)
    created_at = m.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    

class Review(m.Model):
    product = m.ForeignKey(Product, on_delete=m.CASCADE, related_name='reviews')
    rating = m.PositiveIntegerField()  # Assuming rating is an integer
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    date = m.DateTimeField(auto_now_add=True)
    review = m.TextField(null=True, blank=True)

    def __str__(self):
        return f"Review by {self.user} for {self.product.product_name}"

    class Meta:
        db_table = "app_Review"