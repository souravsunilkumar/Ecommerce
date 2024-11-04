from django import forms
from .models import *
from django.forms import inlineformset_factory

class SliderForm(forms.ModelForm):
    class Meta:
        model = slider
        fields = ['Image', 'Discount_Deal', 'Sale', 'Brand_Name', 'Discount', 'Link']

class BannerForm(forms.ModelForm):
    class Meta:
        model = banner_area
        fields = ['image', 'Discount_Deal', 'Quotes', 'Discount', ]

class MainCategoryForm(forms.ModelForm):
    class Meta:
        model = Main_category
        fields = ['name']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['main_category', 'name']

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = Sub_category
        fields = ['category', 'name']

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']

class ColourForm(forms.ModelForm):
    class Meta:
        model = Colour
        fields = ['code']

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'total_quantity', 'availability', 'featured_image', 'product_name',
            'brand', 'price', 'discount', 'tax', 'packing_cost', 'product_information',
            'model_name', 'categories', 'colour', 'tags', 'description', 'section'
        ]

class ProductImageForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all().order_by('-id'),  # Ordering by id in descending order
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Product_Image
        fields = ['product', 'images']


class AdditionalInformationForm(forms.ModelForm):
    class Meta:
        model = Additional_information
        fields = ['product', 'specification', 'detail']

from django import forms



class JobApplicationForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Job_application
        fields = ['first_name', 'last_name', 'date_of_birth', 'phone_number', 'address', 'educational_qualification', 'type_of_job']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'placeholder': 'Your review', 'class': 'comment-input comment-textarea'})
        }